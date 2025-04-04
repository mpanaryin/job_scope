import logging

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import BulkResult
from src.vacancies.application.mappers.mappers import DomainToDBMapper
from src.vacancies.domain.entities import Vacancy
from src.vacancies.domain.interfaces import IVacancyRepository
from src.vacancies.infrastructure.db import orm

logger = logging.getLogger(__name__)


class PGVacancyRepository(IVacancyRepository):
    """Postgresql Vacancy Repository"""
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    async def bulk_create_or_update(self, vacancies: list[Vacancy]) -> BulkResult:
        """
        Добавляет или обновляет вакансии массово
        :param vacancies: Список вакансий для создания
        :return int: Количество обработанных вакансий
        """
        vacancies = DomainToDBMapper().map(vacancies)
        stmt = insert(orm.Vacancy).values([vacancy.model_dump() for vacancy in vacancies])
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
        ).returning(orm.Vacancy.id, orm.Vacancy.updated_at, orm.Vacancy.created_at)
        result = await self.session.execute(stmt)
        rows = result.fetchall()
        logging.info(rows)
        created, updated = 0, 0
        for row in rows:
            if row.updated_at != row.created_at:
                updated += 1
            else:
                created += 1
        return BulkResult(
            success=created+updated,
            failed=len(vacancies) - (created + updated),
        )
