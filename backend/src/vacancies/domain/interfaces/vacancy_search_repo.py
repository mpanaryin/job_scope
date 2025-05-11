import abc

from src.core.domain.entities import BulkResult
from src.vacancies.domain.entities import Vacancy, VacancySearchQuery


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
