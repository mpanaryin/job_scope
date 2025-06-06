from typing import no_type_check, Type, Any, ClassVar, Sequence, TypeVar

from sqladmin.exceptions import InvalidModelError
from sqlalchemy import inspect, Column, Engine, Select, select, and_, or_, ClauseElement
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, ColumnProperty, RelationshipProperty, InstrumentedAttribute, selectinload
from starlette.requests import Request

from src.crud.helpers import get_primary_keys, slugify_class_name, prettify_class_name, get_column_python_type, \
    object_identifier_values, is_falsy_value, get_direction
from src.db.engine import async_session_maker

MODEL_TYPE = TypeVar("ModelType", bound=Any)
MODEL_PROPERTY = ColumnProperty | RelationshipProperty
ENGINE_TYPE = Engine | AsyncEngine
MODEL_ATTR = str | InstrumentedAttribute


class CRUDBaseMeta(type):
    """
    Metaclass used to specify class variables in ModelView.

    Danger:
        This class should almost never be used directly.
    """

    @no_type_check
    def __new__(mcls, name, bases, attrs: dict, **kwargs: Any):
        cls: Type["CRUDBase"] = super().__new__(mcls, name, bases, attrs)

        model = kwargs.get("model")

        if not model:
            return cls

        try:
            inspect(model)
        except NoInspectionAvailable:
            raise InvalidModelError(
                f"Class {model.__name__} is not a SQLAlchemy model."
            )

        cls.pk_columns = get_primary_keys(model)
        cls.identity = slugify_class_name(model.__name__)
        cls.model = model
        cls.session_maker = async_session_maker

        cls.name = attrs.get("name", prettify_class_name(cls.model.__name__))
        cls.name_plural = attrs.get("name_plural", f"{cls.name}s")
        return cls


class CRUDBase(metaclass=CRUDBaseMeta):
    """
    Base class for creating generic CRUD operations using SQLAlchemy models.

    This class is intended to be subclassed with a specific SQLAlchemy model.
    It provides a standard interface for basic database operations and form generation.

    Attributes:
        pk_columns (ClassVar[tuple[Column]]): Primary key columns of the model.
        session_maker (ClassVar): SQLAlchemy session maker (async).
        is_async (ClassVar[bool]): Indicates if async session is used.
        name_plural (ClassVar[str]): Plural name of the model, used in UI.
        form_columns (ClassVar[Sequence[str]]): List of form-included attributes.
        form_excluded_columns (ClassVar[Sequence[str]]): List of form-excluded attributes.
    """
    # Internals
    pk_columns: ClassVar[tuple[Column]]
    session_maker: ClassVar[sessionmaker | async_sessionmaker]
    is_async: ClassVar[bool] = True

    name_plural: ClassVar[str] = ""
    """Plural name of ModelView.
    Default value is Model class name + `s`.
    """

    form_columns: ClassVar[Sequence[MODEL_ATTR]] = []
    """List of columns to include in the form.
    Columns can either be string names or SQLAlchemy columns.

    ???+ note
        By default all columns of Model are included in the form.

    ???+ example
        ```python
        class UserCRUD(CRUDBase, model=User):
            form_columns = [User.name, User.mail]
        ```
    """

    form_excluded_columns: ClassVar[Sequence[MODEL_ATTR]] = []
    """List of columns to exclude from the form.
    Columns can either be string names or SQLAlchemy columns.

    ???+ example
        ```python
        class UserCRUD(CRUDBase, model=User):
            form_excluded_columns = [User.id]
        ```
    """

    def __init__(self):
        self._mapper = inspect(self.model)
        self._prop_names = [attr.key for attr in self._mapper.attrs]
        self._relations = [
            getattr(self.model, relation.key) for relation in self._mapper.relationships
        ]
        self._relation_names = [relation.key for relation in self._mapper.relationships]

        self._form_prop_names = self.get_form_columns()
        self._form_relation_names = [
            name for name in self._form_prop_names if name in self._relation_names
        ]
        self._form_relations = [
            getattr(self.model, name) for name in self._form_relation_names
        ]

    def _get_prop_name(self, prop: MODEL_ATTR) -> str:
        return prop if isinstance(prop, str) else prop.key

    def _build_column_list(
        self,
        defaults: list[str],
        include: str | Sequence[MODEL_ATTR] = None,
        exclude: str | Sequence[MODEL_ATTR] = None,
    ) -> list[str]:
        """This function generalizes constructing a list of columns
        for any sequence of inclusions or exclusions.
        """

        if include == "__all__":
            return self._prop_names
        elif include:
            return [self._get_prop_name(item) for item in include]
        elif exclude:
            exclude = [self._get_prop_name(item) for item in exclude]
            return [prop for prop in self._prop_names if prop not in exclude]
        return defaults

    def get_form_columns(self) -> list[str]:
        """
        Determine which fields to include in the form based on include/exclude configuration.

        :return: List of field names.
        """
        form_columns = getattr(self, "form_columns", None)
        form_excluded_columns = getattr(self, "form_excluded_columns", None)

        return self._build_column_list(
            include=form_columns,
            exclude=form_excluded_columns,
            defaults=self._prop_names,
        )

    async def _run_query(self, stmt: ClauseElement) -> Any:
        """
        Execute a SQLAlchemy select statement asynchronously.

        :param stmt: SQLAlchemy statement to execute.
        :return: List of scalar results.
        """
        async with self.session_maker(expire_on_commit=False) as session:
            result = await session.execute(stmt)
            return result.scalars().unique().all()

    def _get_to_many_stmt(self, relation: MODEL_PROPERTY, values: list[Any]) -> Select:
        target = relation.mapper.class_

        target_pks = get_primary_keys(target)

        if len(target_pks) == 1:
            target_pk = target_pks[0]
            target_pk_type = get_column_python_type(target_pk)
            pk_values = [target_pk_type(value) for value in values]
            return select(target).where(target_pk.in_(pk_values))

        conditions = []
        for value in values:
            conditions.append(
                and_(
                    pk == value
                    for pk, value in zip(
                        target_pks,
                        object_identifier_values(str(value), target),
                    )
                )
            )
        return select(target).where(or_(*conditions))

    def _get_to_one_stmt(self, relation: MODEL_PROPERTY, value: Any) -> Select:
        target = relation.mapper.class_
        target_pks = get_primary_keys(target)
        target_pk_types = [get_column_python_type(pk) for pk in target_pks]
        conditions = [pk == typ(value) for pk, typ in zip(target_pks, target_pk_types)]
        related_stmt = select(target).where(*conditions)
        return related_stmt

    def _stmt_by_identifier(self, identifier: Any) -> Select:
        stmt = select(self.model)
        pks = get_primary_keys(self.model)
        values = object_identifier_values(str(identifier), self.model)
        conditions = [pk == value for (pk, value) in zip(pks, values)]

        return stmt.where(*conditions)

    def _set_many_to_one(self, obj: Any, relation: MODEL_PROPERTY, ident: Any) -> Any:
        values = object_identifier_values(str(ident), relation.entity)
        pks = get_primary_keys(relation.entity)

        # ``relation.local_remote_pairs`` is ordered by the foreign keys
        # but the values are ordered by the primary keys. This dict
        # ensures we write the correct value to the fk fields
        pk_value = {pk: value for pk, value in zip(pks, values)}

        for fk, pk in relation.local_remote_pairs:
            setattr(obj, fk.name, pk_value[pk])

        return obj

    async def _set_attributes_async(
        self, session: AsyncSession, obj: Any, data: dict
    ) -> Any:
        """
        Set model attributes based on input data, including handling of relationships.

        :param session: Async SQLAlchemy session.
        :param obj: Model instance being modified.
        :param data: Data to apply.
        :return: Updated model instance.
        """
        for key, value in data.items():
            column = self._mapper.columns.get(key)
            relation = self._mapper.relationships.get(key)

            # Set falsy values to None, if column is Nullable
            if not value:
                if is_falsy_value(value) and not relation and column.nullable:
                    value = None
                setattr(obj, key, value)
                continue

            if relation:
                direction = get_direction(relation)
                if direction in ["ONETOMANY", "MANYTOMANY"]:
                    related_stmt = self._get_to_many_stmt(relation, value)
                    result = await session.execute(related_stmt)
                    related_objs = result.scalars().all()
                    setattr(obj, key, related_objs)
                elif direction == "ONETOONE":
                    related_stmt = self._get_to_one_stmt(relation, value)
                    result = await session.execute(related_stmt)
                    related_obj = result.scalars().first()
                    setattr(obj, key, related_obj)
                else:
                    obj = self._set_many_to_one(obj, relation, value)
            else:
                setattr(obj, key, value)
        return obj

    def _get_delete_stmt(self, pk: Any) -> Select:
        stmt = select(self.model)
        pks = get_primary_keys(self.model)
        values = object_identifier_values(str(pk), self.model)
        conditions = [pk == value for (pk, value) in zip(pks, values)]
        return stmt.where(*conditions)

    async def on_model_change(
        self, data: dict, model: Any, is_created: bool, request: Request
    ) -> None:
        """
        Hook executed before a model instance is created or updated.

        :param data: Input data dictionary.
        :param model: SQLAlchemy model instance.
        :param is_created: True if the operation is create, False if update.
        :param request: FastAPI Request object.
        """

    async def after_model_change(
        self, data: dict, model: Any, is_created: bool, request: Request
    ) -> None:
        """
        Hook executed after a model instance has been created or updated.

        :param data: Input data dictionary.
        :param model: SQLAlchemy model instance.
        :param is_created: True if the operation is create, False if update.
        :param request: FastAPI Request object.
        """
        # db_obj = await self.get(pk=model.id)
        # for key, value in db_obj.__dict__.items():
        #     setattr(model, key, value)

    async def on_model_delete(self, model: Any, request: Request) -> None:
        """
        Hook executed before a model instance is deleted.

        :param model: SQLAlchemy model instance.
        :param request: FastAPI Request object.
        """

    async def after_model_delete(self, model: Any, request: Request) -> None:
        """
        Hook executed after a model instance is deleted.

        :param model: SQLAlchemy model instance.
        :param request: FastAPI Request object.
        """

    async def create(self, data: dict[str, Any], request: Request) -> Any:
        """
        Create a new model instance in the database.

        :param data: Dictionary containing attributes for the new model.
        :param request: FastAPI Request object, used for context (e.g. user info).
        :return: Created model instance.
        """
        obj = self.model()
        async with self.session_maker(expire_on_commit=False) as session:
            await self.on_model_change(data, obj, True, request)
            obj = await self._set_attributes_async(session, obj, data)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            # await self.after_model_change(data, obj, True, request)
            # obj = await self.get_by_pk(pk=obj.id)
        return obj

    async def get_by_pk(self, pk: Any) -> Any:
        """
        Retrieve a model instance by its primary key.

        :param pk: Primary key or unique identifier.
        :return: Model instance if found, otherwise None.
        """
        stmt = self._stmt_by_identifier(pk)

        for relation in self._form_relations:
            stmt = stmt.options(selectinload(relation))

        async with self.session_maker(expire_on_commit=False) as session:
            result = await session.execute(stmt)
            obj = result.scalars().first()
            return obj

    async def get_multi(self, request: Request, offset: int = 0, limit: int = 100) -> list[Any]:
        """
        Retrieve multiple model instances with optional pagination.

        :param request: FastAPI Request object, used for context.
        :param offset: Number of items to skip (default is 0).
        :param limit: Maximum number of items to return (default is 100).
        :return: List of model instances.
        """
        stmt = select(self.model)

        for relation in self._form_relations:
            stmt = stmt.options(selectinload(relation))

        stmt = stmt.offset(offset).limit(limit)
        db_objs = await self._run_query(stmt)
        return db_objs

    async def update_by_pk(
        self, pk: Any, data: dict[str, Any], request: Request
    ) -> Any:
        """
        Update an existing model instance by primary key.

        :param pk: Primary key or unique identifier of the object to update.
        :param data: Dictionary of fields to update.
        :param request: FastAPI Request object for context-aware logic.
        :return: Updated model instance.
        """
        stmt = self._stmt_by_identifier(pk)

        for relation in self._form_relations:
            stmt = stmt.options(selectinload(relation))

        async with self.session_maker(expire_on_commit=False) as session:
            result = await session.execute(stmt)
            obj = result.scalars().first()
            await self.on_model_change(data, obj, False, request)
            obj = await self._set_attributes_async(session, obj, data)
            await session.commit()
            # await self.after_model_change(data, obj, False, request)
            # obj = await self.get_by_pk(pk=obj.id)
            return obj

    async def delete_by_pk(self, pk: Any, request: Request) -> Any:
        """
        Delete a model instance by primary key.

        :param pk: Primary key or unique identifier of the object to delete.
        :param request: FastAPI Request object for context-aware logic.
        :return: Deleted model instance.
        """
        async with self.session_maker() as session:
            result = await session.execute(self._get_delete_stmt(pk))
            obj = result.scalars().first()
            await self.on_model_delete(obj, request)
            await session.delete(obj)
            await session.commit()
            await self.on_model_delete(obj, request)
            return obj
