from src.core.domain.entities import BulkResult
from src.vacancies.domain.entities import Vacancy
from src.vacancies.domain.interfaces.vacancy_search_repo import IVacancySearchRepository
from src.vacancies.domain.interfaces.vacancy_source_client import TSearchParams, IVacancySourceClient
from src.vacancies.domain.interfaces.vacancy_uow import IVacancyUnitOfWork


async def collect_all_vacancies(
    search_params: TSearchParams,
    client: IVacancySourceClient,
    uow: IVacancyUnitOfWork,
    search_repo: IVacancySearchRepository
) -> dict[str, BulkResult]:
    """
    Collect all vacancies from the external API and save them to both the database and search storage.
    The batch size in search_params doesn't matter. All matching vacancies will be retrieved according to the query.

    :param search_params: Search parameters to pass to the external API.
    :param client: External API client implementing IVacancySourceClient.
    :param uow: Unit of Work to manage transactional operations with the database.
    :param search_repo: Search engine repository (e.g. Elasticsearch) implementing IVacancySearchRepository.
    :return: Dictionary containing bulk operation results for database and search storage.
    """
    vacancies: list[Vacancy] = await client.get_all_vacancies(search_params)

    db_result = await collect_vacancies_to_db(vacancies, uow)
    search_db_result = await collect_vacancies_to_search(vacancies, search_repo)

    statistics = {
        "database": db_result,
        "search_db": search_db_result
    }
    return statistics


async def collect_vacancies(
    search_params: TSearchParams,
    client: IVacancySourceClient,
    uow: IVacancyUnitOfWork,
    search_repo: IVacancySearchRepository
) -> dict[str, BulkResult]:
    """
    Collect vacancies from the external API and save them to both the database and search storage.

    :param search_params: Search parameters to pass to the external API.
    :param client: External API client implementing IVacancySourceClient.
    :param uow: Unit of Work to manage transactional operations with the database.
    :param search_repo: Search engine repository (e.g. Elasticsearch) implementing IVacancySearchRepository.
    :return: Dictionary containing bulk operation results for database and search storage.
    """
    vacancies: list[Vacancy] = await client.get_vacancies(search_params)

    db_result = await collect_vacancies_to_db(vacancies, uow)
    search_db_result = await collect_vacancies_to_search(vacancies, search_repo)

    statistics = {
        "database": db_result,
        "search_db": search_db_result
    }
    return statistics


async def collect_vacancies_to_db(
    vacancies: list[Vacancy],
    uow: IVacancyUnitOfWork
) -> BulkResult:
    """
    Store vacancies in the relational database using the given Unit of Work.

    :param vacancies: List of domain vacancy models to be saved.
    :param uow: Unit of Work to manage the transactional context for database operations.
    :return: Result of bulk insert/update operation.
    """
    async with uow:
        result = await uow.vacancies.bulk_add_or_update(vacancies)
        await uow.commit()
    return result


async def collect_vacancies_to_search(
    vacancies: list[Vacancy],
    search_repo: IVacancySearchRepository
) -> BulkResult:
    """
    Store vacancies in the search database (e.g., Elasticsearch).

    :param vacancies: List of domain vacancy models to be indexed.
    :param search_repo: Repository for managing search engine operations.
    :return: Result of bulk indexing operation.
    """
    result = await search_repo.bulk_add(vacancies)
    return result
