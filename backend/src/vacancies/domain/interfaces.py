import abc

from src.core.schemas import BulkResult
from src.vacancies.domain.entities import Vacancy
from src.vacancies.domain.schemas import VacancyCreate, VacancySearchQuery


class IVacancyRepository(abc.ABC):
    """Репозиторий для основных данных"""

    @abc.abstractmethod
    async def bulk_create_or_update(self, vacancies: list[Vacancy]) -> BulkResult:
        """Множественное создание вакансий или обновление существующих"""
        ...


class IVacancySearchRepository(abc.ABC):
    """Репозиторий для быстрого полнотекстового поиска"""

    @abc.abstractmethod
    async def bulk_create(self, vacancies: list[Vacancy]) -> BulkResult:
        """Множественное создание вакансий"""
        ...

    @abc.abstractmethod
    async def search(self, query: VacancySearchQuery):
        """Поиск вакансий"""
        ...


class IVacancyUnitOfWork(abc.ABC):
    vacancies: IVacancyRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        await self._commit()

    @abc.abstractmethod
    async def _commit(self):
        ...

    @abc.abstractmethod
    async def rollback(self):
        ...
