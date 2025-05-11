import abc
from typing import TypeVar, Generic

from src.vacancies.domain.entities import Vacancy

TSearchParams = TypeVar("TSearchParams")
TVacancy = TypeVar("TVacancy")
TVacancyResponse = TypeVar("TVacancyResponse")


class IVacancySourceClient(abc.ABC, Generic[TSearchParams, TVacancy, TVacancyResponse]):
    """
    Interface for interacting with external job vacancy APIs.

    This contract defines a common interface for clients that fetch job vacancies from third-party APIs.
    It provides methods for both partial and full vacancy retrieval, depending on API capabilities.

    Methods:
        get_vacancies(search_params: TSearchParams) -> list[Vacancy]:
            Fetch a subset of vacancies based on the provided search parameters.

        get_all_vacancies(search_params: TSearchParams) -> list[Vacancy]:
            Fetch all available vacancies for the given parameters.
            Some APIs support only paginated or limited responses; this method
            abstracts away such details and handles complete data collection.
    """

    @abc.abstractmethod
    async def get_vacancies(self, search_params: TSearchParams) -> list[Vacancy]:
        """
        Fetch a subset of vacancies based on the provided search parameters.
        """
        pass

    @abc.abstractmethod
    async def get_all_vacancies(self, search_params: TSearchParams) -> list[Vacancy]:
        """
        Fetch all available vacancies for the given parameters.

        Note: Some APIs support only paginated or limited responses; this method
        abstracts away such details and handles complete data collection.
        """
        pass


