import abc

from src.users.domain.entities import User, UserCreate, UserUpdate


class IUserRepository(abc.ABC):
    """
    Abstract interface for user repository.

    Defines the contract for data access operations related to user entities.
    All implementations must provide persistence-specific logic for managing users.
    """

    @abc.abstractmethod
    def add(self, user: UserCreate) -> User:
        """
        Add a new user to the repository.

        :param user: UserCreate domain model with user creation data.
        :return: The created User entity.
        """
        pass

    @abc.abstractmethod
    async def get_by_email(self, email: str) -> User:
        """
        Retrieve a user by their email address.

        :param email: Email address of the user.
        :return: The corresponding User entity.
        """
        pass

    @abc.abstractmethod
    async def get_by_pk(self, pk: int) -> User:
        """
        Retrieve a user by primary key.

        :param pk: Primary key (ID) of the user.
        :return: The corresponding User entity.
        """
        pass

    @abc.abstractmethod
    async def update(self, user_data: UserUpdate) -> User:
        """
        Update user information.

        :param user_data: Partial data to update the user.
        :return: The updated User entity.
        """
        pass

    @abc.abstractmethod
    async def delete(self, pk: int) -> None:
        """
        Delete a user by primary key.

        :param pk: Primary key (ID) of the user to delete.
        """
        pass


class IUserUnitOfWork(abc.ABC):
    """
    Abstract Unit of Work interface for managing user-related operations.

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
