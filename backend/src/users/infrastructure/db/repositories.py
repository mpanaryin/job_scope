from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.domain.entities import User, UserCreate, UserUpdate
from src.users.domain.exceptions import UserAlreadyExists, UserNotFound
from src.users.domain.interfaces import IUserRepository
from src.users.infrastructure.db.orm import UserDB


class PGUserRepository(IUserRepository):
    """PostgreSQL реализация репозитория пользователей"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    async def add(self, user: UserCreate) -> User:
        """
        Создать нового пользователя.
        Обрабатывает ошибку уникальности и пробрасывает кастомное исключение.
        """
        obj = UserDB(**user.model_dump(mode='json'))
        self.session.add(obj)

        try:
            await self.session.flush()
        except IntegrityError as e:
            # Попытка извлечь поле, вызвавшее нарушение уникальности
            try:
                detail = "User can't be created. " + str(e.orig).split('\nDETAIL:  ')[1]
            except IndexError:
                detail = "User can't be created due to integrity error."
            raise UserAlreadyExists(detail=detail)

        return User(
            id=obj.id,
            email=obj.email,
            hashed_password=obj.hashed_password,
            is_active=obj.is_active,
            is_superuser=obj.is_superuser,
            is_verified=obj.is_verified
        )

    async def get_by_pk(self, pk: int) -> User:
        """
        Получить пользователя по первичному ключу.
        """
        obj = await self.session.get(UserDB, pk)
        if not obj:
            raise UserNotFound(detail=f"User with id {pk} not found")

        return User(
            id=obj.id,
            email=obj.email,
            hashed_password=obj.hashed_password,
            is_active=obj.is_active,
            is_superuser=obj.is_superuser,
            is_verified=obj.is_verified
        )

    async def get_by_email(self, email: str) -> User:
        """
        Получить пользователя по email.
        """
        stmt = select(UserDB).where(UserDB.email == email)
        result = await self.session.execute(stmt)
        obj: UserDB = result.scalar_one_or_none()

        if not obj:
            raise UserNotFound(detail=f"User with email {email} not found")

        return User(
            id=obj.id,
            email=obj.email,
            hashed_password=obj.hashed_password,
            is_active=obj.is_active,
            is_superuser=obj.is_superuser,
            is_verified=obj.is_verified
        )

    async def update(self, user_data: UserUpdate) -> User:
        """
        Обновить данные пользователя.
        """
        stmt = select(UserDB).where(UserDB.id == user_data.id)
        result = await self.session.execute(stmt)
        obj: UserDB = result.scalar_one_or_none()

        if not obj:
            raise UserNotFound(detail=f"User with id {user_data.id} not found")

        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)

        await self.session.flush()

        return User(
            id=obj.id,
            email=obj.email,
            hashed_password=obj.hashed_password,
            is_active=obj.is_active,
            is_superuser=obj.is_superuser,
            is_verified=obj.is_verified
        )

    async def delete(self, pk: int) -> None:
        """
        Удалить пользователя по PK.
        """
        obj = await self.session.get(UserDB, pk)
        if not obj:
            raise UserNotFound(detail=f"User with id {pk} not found")

        await self.session.delete(obj)
