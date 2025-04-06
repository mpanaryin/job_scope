import abc

from src.users.domain.entities import User, UserCreate, UserUpdate


class IUserRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, user: UserCreate) -> User:
        ...

    @abc.abstractmethod
    async def get_by_email(self, email: str) -> User:
        ...

    @abc.abstractmethod
    async def get_by_pk(self, pk: int) -> User:
        ...

    @abc.abstractmethod
    async def update(self, user_data: UserUpdate) -> User:
        ...

    @abc.abstractmethod
    async def delete(self, pk: int) -> None:
        ...


class IUserUnitOfWork(abc.ABC):
    users: IUserRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        await self._commit()

    @abc.abstractmethod
    async def rollback(self):
        ...

    @abc.abstractmethod
    async def _commit(self):
        ...
