import httpx
import pytest

from src.main import app
from src.users.presentation.dependencies import get_user_uow
from tests.users.fakes import FakeUserUnitOfWork


@pytest.mark.asyncio
async def test_me(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json() == {
        'id': None,
        'email': None,
        'is_active': True,
        'is_superuser': False,
        'is_verified': False
    }


@pytest.mark.asyncio
async def test_register(client: httpx.AsyncClient):
    app.dependency_overrides[get_user_uow] = lambda: FakeUserUnitOfWork()

    response = await client.post(
        "/api/users",
        json={
            "email": "user@example.com",
            "password": "securepassword!1",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        },
    )
    assert response.status_code == 200

    new_user_data = response.json()
    assert new_user_data["email"] == "user@example.com"

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_profile(client: httpx.AsyncClient):
    fake_uow = FakeUserUnitOfWork()
    app.dependency_overrides[get_user_uow] = lambda: fake_uow
    try:
        response = await client.get(f"/api/users/{1}")
        assert response.status_code == 404

        response = await client.post(
            "/api/users",
            json={
                "email": "user@example.com",
                "password": "securepassword!1",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
            },
        )
        assert response.status_code == 200
        new_user_data = response.json()

        response = await client.get(f"/api/users/{new_user_data["id"]}")
        assert response.status_code == 200

        data = response.json()
        assert data["email"] == new_user_data["email"]
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_update_user(client: httpx.AsyncClient):
    fake_uow = FakeUserUnitOfWork()
    app.dependency_overrides[get_user_uow] = lambda: fake_uow
    try:
        response = await client.get(f"/api/users/{1}")
        assert response.status_code == 404

        response = await client.post(
            "/api/users",
            json={
                "email": "user@example.com",
                "password": "securepassword!1",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
            },
        )
        assert response.status_code == 200
        new_user_data = response.json()

        response = await client.get(f"/api/users/{new_user_data["id"]}")
        assert response.status_code == 200

        data = response.json()
        assert data["email"] == new_user_data["email"]

        response = await client.patch(
            f"/api/users/{data["id"]}",
            json={
                "email": "user_new@example.com",
            },
        )
        assert response.status_code == 200

        updated_data = response.json()
        assert updated_data["email"] == "user_new@example.com"
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_delete_user(client: httpx.AsyncClient):
    fake_uow = FakeUserUnitOfWork()
    app.dependency_overrides[get_user_uow] = lambda: fake_uow
    try:
        response = await client.get(f"/api/users/{1}")
        assert response.status_code == 404

        response = await client.post(
            "/api/users",
            json={
                "email": "user@example.com",
                "password": "securepassword!1",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
            },
        )
        assert response.status_code == 200
        new_user_data = response.json()

        response = await client.get(f"/api/users/{new_user_data["id"]}")
        assert response.status_code == 200

        response = await client.delete(f"/api/users/{new_user_data["id"]}")
        assert response.status_code == 200
    finally:
        app.dependency_overrides = {}