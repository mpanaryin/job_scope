import httpx
import pytest_asyncio
from sqlalchemy import text

from src.db.engine import engine
from src.users.domain.dtos import UserCreateDTO

TABLES_TO_TRUNCATE = [
    "users",
    "vacancies",
]


@pytest_asyncio.fixture(loop_scope="session")
async def clear_db():
    async with engine.begin() as conn:
        tables = ", ".join(TABLES_TO_TRUNCATE)
        query = f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE;"
        await conn.execute(text(query))


@pytest_asyncio.fixture
def user_factory():
    async def _create(client: httpx.AsyncClient, user: UserCreateDTO) -> dict:
        response = await client.post("/api/users", json=user.model_dump(mode="json"))
        assert response.status_code == 200
        return response.json()
    return _create
