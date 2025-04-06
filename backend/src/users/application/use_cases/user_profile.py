from src.users.domain.entities import User
from src.users.domain.interfaces import IUserUnitOfWork


async def get_user_profile(
    user_pk: int,
    uow: IUserUnitOfWork
) -> User:
    """Получить профиль пользователя по PK"""
    async with uow:
        return await uow.users.get_by_pk(user_pk)
