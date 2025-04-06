from src.users.domain.dtos import UserUpdateDTO
from src.users.domain.entities import User, UserUpdate
from src.users.domain.interfaces import IUserUnitOfWork


async def update_user(
    user_pk: int,
    user_data: UserUpdateDTO,
    uow: IUserUnitOfWork
) -> User:
    """Обновить данные пользователя"""
    user_data = UserUpdate(id=user_pk, **user_data.model_dump(exclude_unset=True))
    async with uow:
        user = await uow.users.update(user_data)
        await uow.commit()
    return user
