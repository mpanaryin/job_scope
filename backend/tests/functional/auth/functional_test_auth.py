import pytest
import httpx

from src.auth.domain.entities import AnonymousUser
from src.auth.presentation.dependencies import get_token_auth
from src.users.domain.entities import UserCreate, User
from src.users.presentation.dependencies import get_user_uow
from tests.utils import override_dependencies

user_create_data = UserCreate(
    email="user@example.com",
    hashed_password="securepassword!1_hashed",
    is_active=True,
    is_superuser=False,
    is_verified=True
)


@pytest.mark.asyncio
async def test_login_success(set_fake_check_password, client: httpx.AsyncClient, mock_auth, fake_user_uow):
    set_fake_check_password(True)
    async with override_dependencies({get_token_auth: lambda: mock_auth, get_user_uow: lambda: fake_user_uow}):
        await fake_user_uow.users.add(user_create_data)

        response = await client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "12345678"
        })
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens set"}
        mock_auth.set_tokens.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_invalid_password(set_fake_check_password, client: httpx.AsyncClient, mock_auth, fake_user_uow):
    set_fake_check_password(False)
    async with override_dependencies({get_token_auth: lambda: mock_auth, get_user_uow: lambda: fake_user_uow}):
        await fake_user_uow.users.add(user_create_data)

        response = await client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "12345678"
        })
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid credentials."}


@pytest.mark.asyncio
async def test_logout(client: httpx.AsyncClient, mock_auth):
    async with override_dependencies({get_token_auth: lambda: mock_auth}):
        response = await client.post("/api/auth/logout")
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens deleted"}
        mock_auth.unset_tokens.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_access_token(client: httpx.AsyncClient, mock_auth):
    async with override_dependencies({get_token_auth: lambda: mock_auth}):
        response = await client.post("/api/auth/refresh")
        assert response.status_code == 200
        assert response.json() == {"detail": "The token has been refresh"}
        mock_auth.refresh_access_token.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_user_tokens_by_superuser(client: httpx.AsyncClient, mock_auth):
    mock_auth.request.state.user = User(
        id=1, email="superuser@mail.com",
        hashed_password="securepassword!1_hashed",
        is_superuser=True, is_verified=True, is_active=True
    )
    async with override_dependencies({get_token_auth: lambda: mock_auth}):
        user_id = 1
        response = await client.post(f"/api/auth/revoke", json={"user_id": user_id})
        assert response.status_code == 200
        assert response.json() == {"detail": f"Tokens revoked for user {user_id}"}
        mock_auth.token_storage.revoke_tokens_by_user.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_user_by_anon(client: httpx.AsyncClient, mock_auth):
    mock_auth.request.state.user = AnonymousUser()
    async with override_dependencies({get_token_auth: lambda: mock_auth}):
        user_id = 1
        response = await client.post(f"/api/auth/revoke", json={"user_id": user_id})
        assert response.status_code == 403
        assert response.json() == {"detail": f"Permission denied"}
