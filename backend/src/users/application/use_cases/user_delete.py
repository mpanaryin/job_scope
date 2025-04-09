from src.users.domain.interfaces import IUserUnitOfWork


async def delete_user(user_pk: int, uow: IUserUnitOfWork) -> None:
    """
    Delete a user by primary key.

    This function deletes a user from the database using the provided unit of work
    and commits the transaction.

    :param user_pk: Primary key of the user to be deleted.
    :param uow: Unit of work instance for handling user repository operations.
    """
    async with uow:
        await uow.users.delete(user_pk)
        await uow.commit()
