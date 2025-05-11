import abc

from src.users.domain.interfaces.user_repo import IUserRepository


class IUserUnitOfWork(abc.ABC):
    """
    Unit of Work interface for managing user-related operations.

    This interface defines the transactional boundary for operations on the user repository.
    It ensures that changes are committed or rolled back as a single unit.

    Attributes:
        users: The repository interface for user operations.
    """

    users: IUserRepository

    async def __aenter__(self):
        """
        Enter the Unit of Work context.

        :return: The Unit of Work instance.
        """
        return self

    async def __aexit__(self, *args):
        """
        Exit the Unit of Work context, rolling back any uncommitted changes.
        """
        await self.rollback()

    async def commit(self):
        """
        Commit all pending changes in the Unit of Work.
        """
        await self._commit()

    @abc.abstractmethod
    async def rollback(self):
        """
        Roll back any uncommitted changes in the Unit of Work.
        """
        pass

    @abc.abstractmethod
    async def _commit(self):
        """
        Internal commit implementation.
        """
        pass
