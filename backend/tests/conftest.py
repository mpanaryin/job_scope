from typing import AsyncIterator

import httpx
import pytest
import pytest_asyncio

from src.main import app
from tests.fakes.users import FakeUserUnitOfWork


@pytest_asyncio.fixture()
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://testserver') as client:
        yield client


@pytest.fixture
def fake_user_uow():
    return FakeUserUnitOfWork()
