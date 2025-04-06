from src.core.schemas import BulkResult
from src.integrations.interfaces import TSearchParams, IVacancySourceClient, TVacancy
from src.vacancies.application.mappers.vacancies import VacancyAPIToDomainMapper
from src.vacancies.domain.entities import Vacancy
from src.vacancies.domain.interfaces import IVacancySearchRepository, IVacancyUnitOfWork


async def collect_all_vacancies(
    search_params: TSearchParams,
    client: IVacancySourceClient,
    uow: IVacancyUnitOfWork,
    search_repo: IVacancySearchRepository
) -> dict[str, BulkResult]:
    """
    Сбор всех вакансий по search_params. Размер выборки в search_params не имеет значения,
    будут получены все возможные вакансии в соответствие запросу.
    :param search_params: Параметры поиска
    :param client: API клиент соответствующего сервиса
    :param uow: Unit of Work для работы с вакансиями
    :param search_repo: Репозиторий документоориентированной базы данных для поиска
    :return dict: Статистика по загруженным данным
    """
    vacancies: list[TVacancy] = await client.get_all_vacancies(search_params)
    vacancies: list[Vacancy] = VacancyAPIToDomainMapper().map(vacancies)
    # Добавление вакансий в базу
    db_result = await collect_vacancies_to_db(vacancies, uow)
    # Добавление вакансий в ElasticSearch
    search_db_result = await collect_vacancies_to_search(vacancies, search_repo)
    # Небольшая статистика по загруженным данным
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
    Сбор всех вакансий по search_params.
    :param search_params: Параметры поиска
    :param client: API клиент соответствующего сервиса
    :param uow: Unit of Work для работы с вакансиями
    :param search_repo: Репозиторий документоориентированной базы данных для поиска
    :return dict: Статистика по загруженным данным
    """
    vacancies: list[TVacancy] = await client.get_vacancies(search_params)
    vacancies: list[Vacancy] = VacancyAPIToDomainMapper().map(vacancies)
    # Добавление вакансий в базу
    db_result = await collect_vacancies_to_db(vacancies, uow)
    # Добавление вакансий в ElasticSearch
    search_db_result = await collect_vacancies_to_search(vacancies, search_repo)
    # Небольшая статистика по загруженным данным
    statistics = {
        "database": db_result,
        "search_db": search_db_result
    }
    return statistics


async def collect_vacancies_to_db(vacancies: list[Vacancy], uow: IVacancyUnitOfWork) -> BulkResult:
    """
    Добавление вакансий в базу данных
    :param vacancies: Список вакансий
    :param uow: Unit of Work для вакансий при работе с БД
    :return int: Общее количество обработанных вакансий
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
    Добавляет вакансии в ElasticSearch или иное документоориентированное хранилище массово
    :param vacancies: Список вакансий, полученных по API
    :param search_repo: Репозиторий для ElasticSearch
    :return: Общее количество обработанных и не обработанных вакансий
    """
    result = await search_repo.bulk_add(vacancies)
    return result
