from typing import Annotated

from fastapi import Depends

from src.vacancies.domain.interfaces.vacancy_search_repo import IVacancySearchRepository
from src.vacancies.domain.interfaces.vacancy_uow import IVacancyUnitOfWork
from src.vacancies.infrastructure.db.unit_of_work import PGVacancyUnitOfWork
from src.vacancies.infrastructure.elastic.repositories import ESVacancySearchRepository


def get_vacancy_uow() -> IVacancyUnitOfWork:
    """
    Dependency provider for the Vacancy Unit of Work.

    Returns a PostgreSQL-based Unit of Work implementation for working with vacancy data.

    :return: An instance of IVacancyUnitOfWork (PGVacancyUnitOfWork).
    """
    return PGVacancyUnitOfWork()


def get_vacancy_search_repo() -> IVacancySearchRepository:
    """
    Dependency provider for the vacancy search repository.

    Returns an implementation of the repository for full-text search,
    based on ElasticSearch.

    :return: An instance of IVacancySearchRepository (ESVacancySearchRepository).
    """
    return ESVacancySearchRepository()


VacancySearchRepoDep = Annotated[IVacancySearchRepository, Depends(get_vacancy_search_repo)]
