from src.users.domain.dtos import UserUpdateDTO
from src.users.domain.entities import User, UserUpdate
from src.users.domain.interfaces import IUserUnitOfWork


async def update_user(
    user_pk: int,
    user_data: UserUpdateDTO,
    uow: IUserUnitOfWork
) -> User:
    """
    Update an existing user's data.

    Applies the given update fields to the user with the specified primary key,
    saves the changes to the database, and commits the transaction.

    :param user_pk: Primary key of the user to update.
    :param user_data: Data transfer object with fields to update.
    :param uow: Unit of work instance for handling user repository operations.
    :return: Updated user object.
    """
    user_data = UserUpdate(id=user_pk, **user_data.model_dump(exclude_unset=True))
    async with uow:
        user = await uow.users.update(user_data)
        await uow.commit()
    return user
