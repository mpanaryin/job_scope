import abc
from typing import TypeVar, Generic

TSearchParams = TypeVar("TSearchParams")
TVacancy = TypeVar("TVacancy")
TVacancyResponse = TypeVar("TVacancyResponse")


class IVacancySourceClient(abc.ABC, Generic[TSearchParams, TVacancy, TVacancyResponse]):
    """Интерфейс взаимодействия с API для получения вакансий"""

    @abc.abstractmethod
    async def get_vacancies(self, search_params: TSearchParams) -> list[TVacancy]:
        """Получение вакансий по указанным параметрам"""
        ...

    @abc.abstractmethod
    async def get_all_vacancies(self, search_params: TSearchParams) -> list[TVacancy]:
        """
        Получение всех вакансий по указанным параметрам

        Note: некоторые API имеют ограничения на выборку, поэтому get_vacancies не может сразу получить всё.
        Из-за этого мы реализуем дополнительный метод для полной выборки.
        """
        ...
