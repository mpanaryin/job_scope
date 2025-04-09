import abc

from src.core.domain.entities import BulkResult
from src.vacancies.domain.entities import Vacancy, VacancySearchQuery


class IVacancyRepository(abc.ABC):
    """
    Repository interface for managing persistent job vacancy data.

    Used for working with the primary data storage (e.g., PostgreSQL).
    """

    @abc.abstractmethod
    async def bulk_add_or_update(self, vacancies: list[Vacancy]) -> BulkResult:
        """
        Create or update multiple vacancies in the persistent store.

        :param vacancies: List of normalized domain vacancies.
        :return: Result summary of the bulk operation.
        """
        pass


class IVacancySearchRepository(abc.ABC):
    """
    Repository interface for full-text job vacancy search.

    Used for interacting with fast-search storage systems (e.g., Elasticsearch).
    """

    @abc.abstractmethod
    async def bulk_add(self, vacancies: list[Vacancy]) -> BulkResult:
        """
        Add multiple vacancies to the search index.

        :param vacancies: List of normalized domain vacancies.
        :return: Result summary of the indexing operation.
        """
        pass

    @abc.abstractmethod
    async def search(self, query: VacancySearchQuery):
        """
        Perform a full-text search over indexed vacancies.

        :param query: Search query object containing filters and terms.
        :return: List of matching search results.
        """
        pass


class IVacancyUnitOfWork(abc.ABC):
    """
    Unit of Work pattern interface for transactional operations on vacancies.

    Provides scoped access to a vacancy repository and ensures consistency
    through commit/rollback semantics.
    """

    vacancies: IVacancyRepository

    async def __aenter__(self):
        """
        Enter the Unit of Work context.

        :return: Self with initialized transactional context.
        """
        return self

    async def __aexit__(self, *args):
        """
        Exit the Unit of Work context and perform rollback if not committed.
        """
        await self.rollback()

    async def commit(self):
        """
        Commit all changes made during the unit of work.
        """
        await self._commit()

    @abc.abstractmethod
    async def _commit(self):
        """
        Persist all changes to the database.
        """
        pass

    @abc.abstractmethod
    async def rollback(self):
        """
        Revert all changes made during the unit of work.
        """
        pass
