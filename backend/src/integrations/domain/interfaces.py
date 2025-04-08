import abc
from typing import TypeVar, Generic

TSearchParams = TypeVar("TSearchParams")
TVacancy = TypeVar("TVacancy")
TVacancyResponse = TypeVar("TVacancyResponse")


class IAsyncHttpClient(abc.ABC):
    """
    Interface for an asynchronous HTTP client.

    This interface defines a standard contract for making HTTP requests asynchronously.
    It abstracts over specific libraries (e.g. aiohttp, httpx) to allow interchangeable implementations.

    Methods:
        get(url: str, **kwargs): Perform an HTTP GET request.
        post(url: str, **kwargs): Perform an HTTP POST request.
        put(url: str, **kwargs): Perform an HTTP PUT request.
        delete(url: str, **kwargs): Perform an HTTP DELETE request.
        patch(url: str, **kwargs): Perform an HTTP PATCH request.
    """

    @abc.abstractmethod
    async def get(self, url: str, **kwargs): ...

    @abc.abstractmethod
    async def post(self, url: str, **kwargs): ...

    @abc.abstractmethod
    async def put(self, url: str, **kwargs): ...

    @abc.abstractmethod
    async def delete(self, url: str, **kwargs): ...

    @abc.abstractmethod
    async def patch(self, url: str, **kwargs): ...


class IVacancySourceClient(abc.ABC, Generic[TSearchParams, TVacancy, TVacancyResponse]):
    """
    Interface for interacting with external job vacancy APIs.

    This contract defines a common interface for clients that fetch job vacancies from third-party APIs.
    It provides methods for both partial and full vacancy retrieval, depending on API capabilities.

    Methods:
        get_vacancies(search_params: TSearchParams) -> list[TVacancy]:
            Fetch a subset of vacancies based on the provided search parameters.

        get_all_vacancies(search_params: TSearchParams) -> list[TVacancy]:
            Fetch all available vacancies for the given parameters.
            Some APIs support only paginated or limited responses; this method
            abstracts away such details and handles complete data collection.
    """

    @abc.abstractmethod
    async def get_vacancies(self, search_params: TSearchParams) -> list[TVacancy]:
        """
        Fetch a subset of vacancies based on the provided search parameters.
        """
        pass

    @abc.abstractmethod
    async def get_all_vacancies(self, search_params: TSearchParams) -> list[TVacancy]:
        """
        Fetch all available vacancies for the given parameters.

        Note: Some APIs support only paginated or limited responses; this method
        abstracts away such details and handles complete data collection.
        """
        pass


