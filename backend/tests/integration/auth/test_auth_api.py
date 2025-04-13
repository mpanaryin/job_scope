import httpx
import pytest

from src.users.domain.dtos import UserCreateDTO

new_user = UserCreateDTO(
    email="new_user@email.com",
    password="Securepassword!1",
    is_active=True, is_verified=True, is_superuser=False
)

new_superuser = UserCreateDTO(
    email="new_superuser@email.com",
    password="Securepassword!2",
    is_active=True, is_verified=True, is_superuser=False
)


@pytest.mark.asyncio(loop_scope="session")
async def test_login_and_logout(clear_db, user_factory):
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        user = await user_factory(client=client, user=new_user)
        assert user["email"] == new_user.email

        login_data = {"email": new_user.email, "password": new_user.password}
        response = await client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens set"}

        response = await client.post("/api/auth/logout")
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens deleted"}


@pytest.mark.asyncio(loop_scope="session")
async def test_login_invalid_password(clear_db, user_factory):
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        user = await user_factory(client=client, user=new_user)
        assert user["email"] == new_user.email

        login_data = {"email": new_user.email, "password": 'pwd_with_error'}
        response = await client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid credentials."}


@pytest.mark.asyncio(loop_scope="session")
async def test_logout(clear_db, user_factory):
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/api/auth/logout")
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens deleted"}


@pytest.mark.asyncio(loop_scope="session")
async def test_login_and_refresh(clear_db, user_factory):
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        user = await user_factory(client=client, user=new_user)
        assert user["email"] == new_user.email

        login_data = {"email": new_user.email, "password": new_user.password}
        response = await client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens set"}

        access_token = response.cookies.get("access_token")
        refresh_token = response.cookies.get("refresh_token")
        client.cookies.set("access_token", access_token)
        client.cookies.set("refresh_token", refresh_token)

        response = await client.post("/api/auth/refresh")
        assert response.status_code == 200
        assert response.json() == {"detail": "The token has been refresh"}
