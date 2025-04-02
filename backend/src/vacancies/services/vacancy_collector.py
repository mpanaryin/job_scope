from elasticsearch import helpers
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.elastic import es_client
from src.db.engine import async_session_maker
from src.integrations.headhunter.schemas.request import HHVacancySearchParams
from src.integrations.headhunter.schemas.response import HHVacancyItem
from src.integrations.headhunter.service import hh_service
from src.vacancies.mappers import hh_vacancy
from src.vacancies.orm import Vacancy
from src.vacancies.schemas import VacancyCreate


async def collect_hh_vacancies(search_params: HHVacancySearchParams):
    """Сбор вакансий из HeadHunter"""
    vacancies: list[HHVacancyItem] = await hh_service.get_all_vacancies(search_params)

    # Добавление вакансий в базу
    success_pg = await collect_hh_vacancies_to_db(vacancies)
    # Добавление вакансий в ElasticSearch
    success_es, failed_es = await collect_hh_vacancies_to_es(vacancies)

    # Небольшая статистика по загруженным данным
    statistics = {
        "postgresql": success_pg,
        "elastic": {
            "success": success_es,
            "failed": failed_es
        }
    }
    return statistics


async def collect_hh_vacancies_to_db(vacancies: list[HHVacancyItem]):
    """Добавление вакансий в базу"""
    db_vacancies = hh_vacancy.map_hh_vacancies_to_domain_vacancies(vacancies)
    async with async_session_maker(expire_on_commit=False) as session:
        success_pg = await bulk_add_vacancies_to_db(db_vacancies, db=session)
    return success_pg


async def collect_hh_vacancies_to_es(vacancies: list[HHVacancyItem]):
    """Добавление вакансий в ElasticSearch"""
    db_vacancies = hh_vacancy.map_hh_vacancies_to_domain_vacancies(vacancies)
    async with async_session_maker(expire_on_commit=False) as session:
        success_pg = await bulk_add_vacancies_to_db(db_vacancies, db=session)
    return success_pg


async def bulk_add_vacancies_to_es(vacancies: list[dict]):
    """Добавляет вакансии в ElasticSearch массово"""
    success, failed = await helpers.async_bulk(es_client, vacancies)
    return success, failed


async def bulk_add_vacancies_to_db(vacancies: list[VacancyCreate], db: AsyncSession):
    """Добавляет вакансии в PostgreSQL массово"""
    stmt = insert(Vacancy).values([vacancy.model_dump() for vacancy in vacancies])
    stmt = stmt.on_conflict_do_update(
        index_elements=["source_name", "source_id"],
        set_={
            "url": stmt.excluded.url,
            "name": stmt.excluded.name,
            "description": stmt.excluded.description,
            "salary_from": stmt.excluded.salary_from,
            "salary_to": stmt.excluded.salary_to,
            "salary_currency": stmt.excluded.salary_currency,
            "salary_gross": stmt.excluded.salary_gross,
            "published_at": stmt.excluded.published_at,
            "area_name": stmt.excluded.area_name,
            "employer_name": stmt.excluded.employer_name,
            "employment": stmt.excluded.employment,
            "experience": stmt.excluded.experience,
            "schedule": stmt.excluded.schedule,
            "has_test": stmt.excluded.has_test,
            "is_archived": stmt.excluded.is_archived,
            "type": stmt.excluded.type,
            "meta": stmt.excluded.meta,
        },
    )
    await db.execute(stmt)
    await db.commit()
    return len(vacancies)
