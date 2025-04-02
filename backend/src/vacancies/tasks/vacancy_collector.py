import logging

from asgiref.sync import async_to_sync
from celery import shared_task

from src.integrations.headhunter.schemas.request import HHVacancySearchParams
from src.vacancies.services.vacancy_collector import collect_hh_vacancies

logger = logging.getLogger(__name__)


@shared_task
def collect_vacancies_task():
    """Задача для выполнения в фоне с целью получения актуальных вакансий headhunter"""
    python_backend_params = HHVacancySearchParams(
        page=0,
        per_page=1,
        text='Backend python developer',
        area=['1'],  # Moscow,
        order_by='publication_time'
    )
    # result = async_to_sync(collect_vacancies)(python_backend_params)
    # return result
