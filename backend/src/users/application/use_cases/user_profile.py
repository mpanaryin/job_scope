from src.users.domain.entities import User
from src.users.domain.interfaces import IUserUnitOfWork


async def get_user_profile(
    user_pk: int,
    uow: IUserUnitOfWork
) -> User:
    """
    Retrieve a user profile by primary key.

    :param user_pk: Primary key of the user.
    :param uow: Unit of work instance for handling user repository operations.
    :return: User object corresponding to the provided primary key.
    """
    async with uow:
        return await uow.users.get_by_pk(user_pk)
