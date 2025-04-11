import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock

from src.auth.domain.entities import AnonymousUser
from src.main import app
from src.auth.presentation.dependencies import get_token_auth
from src.users.domain.entities import UserCreate, User
from src.users.presentation.dependencies import get_user_uow
from tests.users.fakes import FakeUserUnitOfWork


@pytest.mark.asyncio
async def test_login_success(monkeypatch, client: httpx.AsyncClient):
    monkeypatch.setattr(
        "src.auth.application.use_cases.authentication.check_password",
        lambda password, hashed: True
    )
    mock_auth = MagicMock()
    mock_auth.set_tokens = AsyncMock()
    app.dependency_overrides[get_token_auth] = lambda: mock_auth
    app.dependency_overrides[get_user_uow] = lambda: fake_uow
    try:
        fake_uow = FakeUserUnitOfWork()
        user_data = UserCreate(
            email="user@example.com",
            hashed_password="securepassword!1_hashed",
            is_active=True,
            is_superuser=False,
            is_verified=True
        )
        await fake_uow.users.add(user_data)

        response = await client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "12345678"
        })
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens set"}
        mock_auth.set_tokens.assert_awaited_once()
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_login_invalid_password(monkeypatch, client: httpx.AsyncClient):
    monkeypatch.setattr(
        "src.auth.application.use_cases.authentication.check_password",
        lambda password, hashed: False
    )
    mock_auth = MagicMock()
    mock_auth.set_tokens = AsyncMock()
    app.dependency_overrides[get_token_auth] = lambda: mock_auth
    app.dependency_overrides[get_user_uow] = lambda: fake_uow
    try:
        fake_uow = FakeUserUnitOfWork()
        user_data = UserCreate(
            email="user@example.com",
            hashed_password="securepassword!1_hashed",
            is_active=True,
            is_superuser=False,
            is_verified=True
        )
        await fake_uow.users.add(user_data)

        response = await client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "12345678"
        })
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid credentials."}
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_logout(client: httpx.AsyncClient):
    mock_auth = MagicMock()
    mock_auth.unset_tokens = AsyncMock()
    app.dependency_overrides[get_token_auth] = lambda: mock_auth
    try:
        response = await client.post("/api/auth/logout")
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens deleted"}
        mock_auth.unset_tokens.assert_awaited_once()
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_refresh_access_token(client: httpx.AsyncClient):
    mock_auth = MagicMock()
    mock_auth.refresh_access_token = AsyncMock()
    app.dependency_overrides[get_token_auth] = lambda: mock_auth
    try:
        response = await client.post("/api/auth/refresh")
        assert response.status_code == 200
        assert response.json() == {"detail": "The token has been refresh"}
        mock_auth.refresh_access_token.assert_awaited_once()
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_revoke_user_tokens_by_superuser(client: httpx.AsyncClient):
    mock_auth = MagicMock()
    mock_auth.token_storage = MagicMock()
    mock_auth.token_storage.revoke_tokens_by_user = AsyncMock()
    mock_auth.request.state.user = User(
        id=1, email="superuser@mail.com",
        hashed_password="securepassword!1_hashed",
        is_superuser=True, is_verified=True, is_active=True
    )
    app.dependency_overrides[get_token_auth] = lambda: mock_auth
    try:
        user_id = 1
        response = await client.post(f"/api/auth/revoke", json={"user_id": user_id})
        assert response.status_code == 200
        assert response.json() == {"detail": f"Tokens revoked for user {user_id}"}
        mock_auth.token_storage.revoke_tokens_by_user.assert_awaited_once()
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_revoke_user_by_anon(client: httpx.AsyncClient):
    mock_auth = MagicMock()
    mock_auth.token_storage = MagicMock()
    mock_auth.token_storage.revoke_tokens_by_user = AsyncMock()
    mock_auth.request.state.user = AnonymousUser()
    app.dependency_overrides[get_token_auth] = lambda: mock_auth
    try:
        user_id = 1
        response = await client.post(f"/api/auth/revoke", json={"user_id": user_id})
        assert response.status_code == 403
        assert response.json() == {"detail": f"Permission denied"}
    finally:
        app.dependency_overrides = {}
