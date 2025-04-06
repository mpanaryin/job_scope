from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import async_session_maker
from src.users.domain.interfaces import IUserUnitOfWork
from src.users.infrastructure.db.repositories import PGUserRepository


class PGUserUnitOfWork(IUserUnitOfWork):
    def __init__(self, session_factory=async_session_maker):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.users = PGUserRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
