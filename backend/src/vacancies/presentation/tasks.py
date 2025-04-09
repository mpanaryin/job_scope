import logging

from asgiref.sync import async_to_sync
from celery import shared_task

from src.integrations.infrastructure.headhunter.contracts.request import HHVacancySearchParams
from src.vacancies.application.use_cases.vacancy_collector import collect_vacancies
from src.vacancies.presentation.dependencies import get_headhunter_client, get_vacancy_search_repo, get_vacancy_uow

logger = logging.getLogger(__name__)


@shared_task
def collect_vacancies_task() -> dict:
    """
    Celery task to collect vacancies from HeadHunter.

    This background task performs the following:
    - Queries HeadHunter API with specific search parameters.
    - Saves data in both relational DB and ElasticSearch.
    - Returns a summary of processed results.

    :return: Dictionary containing the number of processed items for each storage layer.
    """
    # Example search parameters for Python backend developer in Moscow
    python_backend_params = HHVacancySearchParams(
        page=0,
        per_page=1,
        text='Backend python developer',
        area=['1'],  # Moscow,
        order_by='publication_time'
    )
    result = async_to_sync(collect_vacancies)(
        python_backend_params,
        get_headhunter_client(),
        get_vacancy_uow(),
        get_vacancy_search_repo()
    )
    return {key: value.model_dump(mode="json") for key, value in result.items()}

