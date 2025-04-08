from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an asynchronous SQLAlchemy session.

    This function is used in FastAPI dependencies to inject a database session into route handlers
    or other components.
    It ensures proper session lifecycle management with context control.

    Yields:
        AsyncSession: SQLAlchemy async session.
    """
    async with async_session_maker() as session:
        yield session

# Shortcut type annotation for injecting the async session via Depends
DBAsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
