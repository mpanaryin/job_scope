from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

DBAsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
