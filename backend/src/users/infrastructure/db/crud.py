from typing import Any
from urllib.request import Request

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.users.infrastructure.db import orm
from src.auth.infrastructure.services.password import hash_password
from src.crud.base import CRUDBase


class UserService(CRUDBase, model=orm.UserDB):
    """
    Service for managing user-related database operations.

    Inherits from CRUDBase and provides user-specific implementations
    for creating and retrieving user records.
    """

    async def create(self, data: dict[str, Any], request: Request | None = None) -> orm.UserDB:
        """
        Create a new user record with hashed password.

        :param data: Dictionary of user fields, including raw password.
        :param request: Optional FastAPI request object used for lifecycle hooks.
        :return: The created UserDB instance.
        """
        password = data.pop("password", "")
        obj = self.model(**data)
        async with self.session_maker(expire_on_commit=False) as session:
            obj.hashed_password = hash_password(password)
            session.add(obj)
            await session.commit()
            if request:
                await self.after_model_change(data, obj, True, request)
        return obj

    async def get_by_email(self, email: str) -> orm.UserDB:
        """
        Retrieve a user by email address.

        :param email: Email address of the user to retrieve.
        :return: A UserDB instance if found, otherwise None.
        """
        stmt = select(self.model).where(self.model.email == email).limit(1)

        for relation in self._form_relations:
            stmt = stmt.options(selectinload(relation))

        async with self.session_maker(expire_on_commit=False) as session:
            result = await session.execute(stmt)
            obj = result.scalars().first()
            return obj
