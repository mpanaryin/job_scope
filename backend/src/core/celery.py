import os
from celery import Celery
from celery.signals import setup_logging

celery_app = Celery(
    "core",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND")
)


@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig  # noqa
    from src.core.logging_setup import LOGGING_CONFIG  # noqa

    dictConfig(LOGGING_CONFIG)


celery_app.autodiscover_tasks(["src.vacancies.tasks.vacancy_collector"])

# Настройки Celery Beat (задачи по расписанию)
celery_app.conf.beat_schedule = {
    "fetch_vacancies_every_10_min": {
        "task": "src.vacancies.tasks.vacancy_collector.collect_vacancies_task",
        "schedule": 60.0  # каждые 1 мин
    }
}
