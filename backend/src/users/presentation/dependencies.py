from typing import Annotated

from fastapi import Depends

from src.users.domain.interfaces import IUserUnitOfWork
from src.users.infrastructure.db.unit_of_work import PGUserUnitOfWork


def get_user_uow() -> IUserUnitOfWork:
    """
    Dependency that provides an instance of IUserUnitOfWork.

    This allows the presentation layer to remain decoupled from the actual implementation.
    By default, it returns a PostgreSQL-based unit of work (PGUserUnitOfWork), but the implementation
    can be easily overridden for testing or different environments.

    :return: IUserUnitOfWork instance.
    """
    return PGUserUnitOfWork()


UserUoWDep = Annotated[IUserUnitOfWork, Depends(get_user_uow)]
