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
    """
    Configure Celery logging using the app's standard logging setup.
    This disables Celery's default logger configuration.
    """
    from logging.config import dictConfig  # noqa
    from src.core.infrastructure.logging_setup import LOGGING_CONFIG  # noqa

    dictConfig(LOGGING_CONFIG)


# Automatically discover tasks
celery_app.autodiscover_tasks(["src.vacancies.presentation.tasks"])

# Optional Celery Beat configuration for periodic tasks
# Uncomment and adjust the schedule as needed
# celery_app.conf.beat_schedule = {
#     "fetch_vacancies_every_10_min": {
#         "task": "src.vacancies.presentation.tasks.collect_vacancies_task",
#         "schedule": 60.0  # каждые 1 мин
#     }
# }
