from src.users.domain.interfaces import IUserUnitOfWork


async def delete_user(user_pk: int, uow: IUserUnitOfWork) -> None:
    """Удалить пользователя по PK"""
    async with uow:
        await uow.users.delete(user_pk)
        await uow.commit()
