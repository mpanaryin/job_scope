import httpx
import pytest
from starlette.middleware import Middleware

from src.auth.presentation.middlewares import SecurityMiddleware
from src.main import app
from src.vacancies.presentation.dependencies import get_vacancy_search_repo
from tests.fakes.vacancies import FakeSearchVacancyRepository


@pytest.mark.asyncio
async def test_search_vacancies(client: httpx.AsyncClient):
    """
    Test the vacancy search endpoint without authentication.

    Temporarily disables security middleware and overrides the search repository
    with a fake implementation to verify that the search endpoint responds successfully.
    """
    # Will require user authentication unless disabled
    app.user_middleware = [
        m for m in app.user_middleware if m.cls.__name__ != "SecurityMiddleware"
    ]
    app.middleware_stack = app.build_middleware_stack()

    try:
        fake_repo = FakeSearchVacancyRepository()
        app.dependency_overrides[get_vacancy_search_repo] = lambda: fake_repo

        response = await client.get(f"/api/vacancies/search", params={
            "query": "python"
        })
        assert response.status_code == 200
    finally:
        app.dependency_overrides = {}
        app.user_middleware.append(Middleware(SecurityMiddleware))
        app.middleware_stack = app.build_middleware_stack()
