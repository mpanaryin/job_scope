from src.integrations.infrastructure.headhunter.client import HeadHunterClient
from src.vacancies.infrastructure.db.unit_of_work import PGVacancyUnitOfWork
from src.vacancies.infrastructure.elastic.repositories import ESVacancySearchRepository


def get_vacancy_uow() -> PGVacancyUnitOfWork:
    """Получить UoW для вакансий"""
    return PGVacancyUnitOfWork()


def get_vacancy_search_repo() -> ESVacancySearchRepository:
    """Получить репозиторий для работы с полнотекстовым поиском по вакансиям"""
    return ESVacancySearchRepository()


def get_headhunter_client() -> HeadHunterClient:
    """Получить клиент для работы с HeadHunter API"""
    return HeadHunterClient()
