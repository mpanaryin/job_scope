from typing import Callable, TypeVar, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request

from src.auth.presentation.permissions import access_control
from src.core.domain.exceptions import AlreadyExists, NotFound
from src.crud.base import CRUDBase

Schema = TypeVar("Schema", bound=BaseModel)


class CRUDRouter:
    """
    A generic CRUD router generator for FastAPI.

    Automatically generates standard REST endpoints (create, read, update, delete)
    based on a given CRUD service and Pydantic contracts.

    Attributes:
        crud (CRUDBase): The service class responsible for database operations.
        create_schema (Type[BaseModel]): Schema for data creation.
        update_schema (Type[BaseModel]): Schema for data update.
        read_schema (Type[BaseModel]): Schema for response serialization.
        router (APIRouter): FastAPI router where endpoints will be registered.
        methods (list[str]): Allowed HTTP methods (GET, POST, PUT, DELETE).
        create_as_form (bool): Whether to use form-based data parsing for creation.
        update_as_form (bool): Whether to use form-based data parsing for updating.
        access_control (access_control): Access control decorator for endpoints.
    """
    crud: CRUDBase
    create_schema: Schema
    update_schema: Schema
    read_schema: Schema
    router: APIRouter
    methods: list[str] = frozenset(["GET", "POST", "PUT", "DELETE"])
    create_as_form: bool = False
    update_as_form: bool = False
    access_control: access_control = access_control(superuser=True)

    def create(self) -> Callable:
        """
        Register POST / endpoint to create a new object.

        Returns:
            Callable: FastAPI route handler function.
        """
        if self.create_as_form:
            @self.router.post("/", response_model=self.read_schema)
            @self.access_control
            async def _create(request: Request, obj: self.create_schema = Depends(self.create_schema.as_form)):
                try:
                    db_obj = await self.crud.create(data=obj.model_dump(), request=request)
                except IntegrityError:
                    raise AlreadyExists()
                return db_obj
        else:
            @self.router.post("/", response_model=self.read_schema)
            @self.access_control
            async def _create(request: Request, obj: self.create_schema):
                try:
                    db_obj = await self.crud.create(data=obj.model_dump(), request=request)
                except IntegrityError:
                    raise AlreadyExists()
                return db_obj
        return _create

    def get_by_pk(self) -> Callable:
        """
        Register GET /{pk} endpoint to retrieve an object by its primary key.

        Returns:
            Callable: FastAPI route handler function.
        """
        @self.router.get("/{pk}", response_model=self.read_schema)
        @self.access_control
        async def _get(request: Request, pk: Any):
            db_obj = await self.crud.get_by_pk(pk=pk)
            if not db_obj:
                raise NotFound()
            return db_obj
        return _get

    def get_multi(self) -> Callable:
        """
        Register GET / endpoint to retrieve a list of objects with pagination.

        Returns:
            Callable: FastAPI route handler function.
        """
        @self.router.get("/", response_model=list[self.read_schema])
        @self.access_control
        async def _get_multi(request: Request, offset: int = 0, limit: int = 100):
            db_objs = await self.crud.get_multi(request, offset, limit)
            return db_objs
        return _get_multi

    def update_by_pk(self) -> Callable:
        """
        Register PATCH /{pk} endpoint to update an object by its primary key.

        Returns:
            Callable: FastAPI route handler function.
        """
        if self.update_as_form:
            @self.router.patch("/{pk}", response_model=self.read_schema)
            @self.access_control
            async def _update(request: Request, pk: Any, obj: self.update_schema = Depends(self.update_schema.as_form)):
                try:
                    db_obj = await self.crud.update_by_pk(
                        pk=pk,
                        data=obj.model_dump(exclude_unset=True),
                        request=request
                    )
                except AttributeError:
                    raise NotFound()
                return db_obj
        else:
            @self.router.patch("/{pk}", response_model=self.read_schema)
            @self.access_control
            async def _update(request: Request, pk: Any, obj: self.update_schema):
                try:
                    db_obj = await self.crud.update_by_pk(
                        pk=pk,
                        data=obj.model_dump(exclude_unset=True),
                        request=request
                    )
                except AttributeError:
                    raise NotFound()
                return db_obj
        return _update

    def delete_by_pk(self) -> Callable:
        """
        Register DELETE /{pk} endpoint to delete an object by its primary key.

        Returns:
            Callable: FastAPI route handler function.
        """
        @self.router.delete("/{pk}", response_model=self.read_schema)
        @self.access_control
        async def _delete(request: Request, pk: Any):
            db_obj = await self.crud.delete_by_pk(pk=pk, request=request)
            return db_obj
        return _delete

    def init_router(self):
        """
        Initialize the router by registering CRUD endpoints based on allowed methods.
        """
        if 'POST' in self.methods:
            self.create()
        if 'GET' in self.methods:
            self.get_multi()
            self.get_by_pk()
        if 'PUT' in self.methods:
            self.update_by_pk()
        if 'DELETE' in self.methods:
            self.delete_by_pk()

    def get_router(self):
        """
        Get the fully initialized FastAPI router.

        Returns:
            APIRouter: The configured FastAPI router instance.
        """
        self.init_router()
        return self.router
