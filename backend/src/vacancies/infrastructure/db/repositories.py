import logging
from typing import Any, Sequence

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.domain.entities import BulkResult
from src.vacancies.application.mappers.vacancies import VacancyDomainToDTOMapper
from src.vacancies.domain.entities import Vacancy
from src.vacancies.domain.interfaces import IVacancyRepository
from src.vacancies.infrastructure.db import orm

logger = logging.getLogger(__name__)


class PGVacancyRepository(IVacancyRepository):
    """
    PostgreSQL implementation of the Vacancy repository.

    Handles bulk insert and update operations for normalized domain vacancies
    using PostgreSQL's ON CONFLICT clause to prevent duplicates.

    Attributes:
        session (AsyncSession): Active SQLAlchemy asynchronous session.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository with an active database session.

        :param session: Async SQLAlchemy session used for executing queries.
        """
        super().__init__()
        self.session = session

    async def bulk_add_or_update(self, vacancies: list[Vacancy]) -> BulkResult:
        """
        Bulk insert or update vacancy records in the database.

        Uses PostgreSQL `ON CONFLICT DO UPDATE` to either create new records
        or update existing ones based on (source_name, source_id).

        :param vacancies: List of normalized Vacancy domain models.
        :return: BulkResult summarizing the number of created and updated rows.
        """
        vacancies = VacancyDomainToDTOMapper().map(vacancies)
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
        return self._build_bulk_result(rows, total=len(vacancies))

    def _build_bulk_result(self, rows: Sequence[Any], total: int) -> BulkResult:
        """
        Determine how many records were created vs updated.

        Compares `created_at` and `updated_at` timestamps to distinguish between insert and update operations.

        :param rows: List of returned rows with created_at and updated_at fields.
        :param total: Total number of records processed.
        :return: BulkResult with count of successful and failed operations.
        """
        created, updated = 0, 0
        for row in rows:
            if row.updated_at != row.created_at:
                updated += 1
            else:
                created += 1
        return BulkResult(
            success=created + updated,
            failed=total - (created + updated),
            total=total
        )
