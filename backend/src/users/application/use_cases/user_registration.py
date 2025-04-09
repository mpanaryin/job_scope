from src.auth.infrastructure.services.password import hash_password
from src.users.domain.entities import UserCreate, User
from src.users.domain.interfaces import IUserUnitOfWork
from src.users.domain.dtos import UserCreateDTO


async def register_user(
    user_data: UserCreateDTO,
    uow: IUserUnitOfWork,
) -> User:
    """
    Register a new user in the system.

    This function hashes the password, creates a new user entity,
    saves it to the database, and commits the transaction.

    :param user_data: Data transfer object containing user registration details.
    :param uow: Unit of work instance for handling user repository operations.
    :return: Newly created user object.
    """
    user_data = UserCreate(
        **user_data.model_dump(mode='json'),
        hashed_password=hash_password(user_data.password)
    )
    async with uow:
        new_user = await uow.users.add(user_data)
        await uow.commit()
    return new_user
