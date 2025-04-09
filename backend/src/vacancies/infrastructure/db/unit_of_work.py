from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import async_session_maker
from src.vacancies.domain.interfaces import IVacancyUnitOfWork
from src.vacancies.infrastructure.db.repositories import PGVacancyRepository


class PGVacancyUnitOfWork(IVacancyUnitOfWork):
    """
    PostgreSQL Unit of Work implementation for Vacancy operations.

    Manages a transactional context for interacting with the vacancy repository.
    Commits or rolls back all operations within the unit of work scope.

    Attributes:
        session_factory: A callable that returns an AsyncSession.
        session: Active asynchronous session for database interactions.
        vacancies: Repository for vacancy-related database operations.
    """

    def __init__(self, session_factory=async_session_maker):
        """
        Initialize the unit of work with a session factory.

        :param session_factory: Callable that returns an AsyncSession.
        """
        self.session_factory = session_factory

    async def __aenter__(self):
        """
        Enter the async context and initialize the session and repositories.
        """
        self.session: AsyncSession = self.session_factory()
        self.vacancies = PGVacancyRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        """
        Exit the async context and ensure the session is closed.
        """
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        """
        Commit the current transaction.
        """
        await self.session.commit()

    async def rollback(self):
        """
        Rollback the current transaction.
        """
        await self.session.rollback()
