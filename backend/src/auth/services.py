from typing import Any, Dict
from urllib.request import Request

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.auth import orm
from src.auth.exceptions import InvalidCredentials
from src.auth.schemas import AuthUser
from src.auth.utils import check_password, hash_password
from src.crud.base import CRUDBase


class UserService(CRUDBase, model=orm.User):

    async def create(self, data: Dict[str, Any], request: Request | None = None) -> Any:
        password = data.pop("password", "")
        obj = self.model(**data)
        async with self.session_maker(expire_on_commit=False) as session:
            obj.hashed_password = hash_password(password).decode('utf-8')
            session.add(obj)
            await session.commit()
            if request:
                await self.after_model_change(data, obj, True, request)
        return obj

    async def get_by_email(self, email: str) -> Any:
        """Get the model object"""
        stmt = select(self.model).where(self.model.email == email).limit(1)

        for relation in self._form_relations:
            stmt = stmt.options(selectinload(relation))

        async with self.session_maker(expire_on_commit=False) as session:
            result = await session.execute(stmt)
            obj = result.scalars().first()
            return obj


async def authenticate(credentials: AuthUser):
    """Аутентификация пользователя"""
    user = await UserService().get_by_email(credentials.email)
    if not user:
        raise InvalidCredentials()

    if not check_password(credentials.password, user.hashed_password):
        raise InvalidCredentials()
    return user
