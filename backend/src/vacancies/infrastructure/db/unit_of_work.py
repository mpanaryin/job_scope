from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import async_session_maker
from src.vacancies.domain.interfaces import IVacancyUnitOfWork
from src.vacancies.infrastructure.db.repositories import PGVacancyRepository


class PGVacancyUnitOfWork(IVacancyUnitOfWork):
    def __init__(self, session_factory=async_session_maker):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.vacancies = PGVacancyRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
