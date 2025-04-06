from typing import Any
from urllib.request import Request

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.users.infrastructure.db import orm
from src.auth.infrastructure.services.password_utils import hash_password
from src.crud.base import CRUDBase


class UserService(CRUDBase, model=orm.UserDB):

    async def create(self, data: dict[str, Any], request: Request | None = None) -> orm.UserDB:
        password = data.pop("password", "")
        obj = self.model(**data)
        async with self.session_maker(expire_on_commit=False) as session:
            obj.hashed_password = hash_password(password).decode('utf-8')
            session.add(obj)
            await session.commit()
            if request:
                await self.after_model_change(data, obj, True, request)
        return obj

    async def get_by_email(self, email: str) -> orm.UserDB:
        """Get the model object"""
        stmt = select(self.model).where(self.model.email == email).limit(1)

        for relation in self._form_relations:
            stmt = stmt.options(selectinload(relation))

        async with self.session_maker(expire_on_commit=False) as session:
            result = await session.execute(stmt)
            obj = result.scalars().first()
            return obj
