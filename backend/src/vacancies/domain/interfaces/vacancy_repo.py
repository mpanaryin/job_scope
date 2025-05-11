import abc

from src.core.domain.entities import BulkResult
from src.vacancies.domain.entities import Vacancy


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
