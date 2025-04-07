from src.auth.infrastructure.services.password import hash_password
from src.users.domain.entities import UserCreate, User
from src.users.domain.interfaces import IUserUnitOfWork
from src.users.domain.dtos import UserCreateDTO


async def register_user(
    user_data: UserCreateDTO,
    uow: IUserUnitOfWork,
) -> User:
    """Регистрация пользователя в системе"""
    user_data = UserCreate(
        **user_data.model_dump(mode='json'),
        hashed_password=hash_password(user_data.password).decode('utf-8')
    )
    async with uow:
        new_user = await uow.users.add(user_data)
        await uow.commit()
    return new_user
