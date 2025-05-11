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
    is_active=True, is_verified=True, is_superuser=True
)


@pytest.mark.asyncio(loop_scope="session")
async def test_login_and_logout(clear_db, user_factory):
    """
    Test successful login and logout flow.

    Verifies that a registered user can log in and receive tokens,
    and that logout successfully clears them.
    """
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        await user_factory(client=client, user=new_user)

        login_data = {"email": new_user.email, "password": new_user.password}
        await _login_and_set_cookies(client, login_data)

        response = await client.post("/api/auth/logout")
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens deleted"}


@pytest.mark.asyncio(loop_scope="session")
async def test_login_invalid_password(clear_db, user_factory):
    """
    Test login with an incorrect password.

    Ensures that the API returns 401 with a proper error message.
    """
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        await user_factory(client=client, user=new_user)

        login_data = {"email": new_user.email, "password": 'pwd_with_error'}
        response = await client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid credentials."}


@pytest.mark.asyncio(loop_scope="session")
async def test_logout(clear_db, user_factory):
    """
    Test logout without being logged in.

    Ensures that the logout endpoint returns a valid response even if no tokens are set.
    """
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/api/auth/logout")
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens deleted"}


@pytest.mark.asyncio(loop_scope="session")
async def test_login_and_refresh(clear_db, user_factory):
    """
    Test the token refresh endpoint after a successful login.

    Verifies that the refresh token is accepted and a new access token is issued.
    """
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        await user_factory(client=client, user=new_user)

        login_data = {"email": new_user.email, "password": new_user.password}
        await _login_and_set_cookies(client, login_data)

        response = await client.post("/api/auth/refresh")
        assert response.status_code == 200
        assert response.json() == {"detail": "The token has been refresh"}


@pytest.mark.asyncio(loop_scope="session")
async def test_revoke_by_ordinary_user(clear_db, user_factory):
    """
    Test that an ordinary user cannot revoke tokens for another user.

    Ensures that only superusers are authorized to call the revoke endpoint.
    """
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        user = await user_factory(client=client, user=new_user)

        login_data = {"email": new_user.email, "password": new_user.password}
        await _login_and_set_cookies(client, login_data)

        response = await client.post("/api/auth/revoke", json={"user_id": user["id"]})
        assert response.status_code == 403
        assert response.json() == {"detail": f"Permission denied"}


@pytest.mark.asyncio(loop_scope="session")
async def test_revoke_by_superuser(clear_db, user_factory):
    """
    Test that a superuser can revoke tokens for a user.

    Verifies proper access control and expected API response.
    """
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        user = await user_factory(client=client, user=new_superuser)
        assert user["email"] == new_superuser.email

        login_data = {"email": new_superuser.email, "password": new_superuser.password}
        await _login_and_set_cookies(client, login_data)

        response = await client.post("/api/auth/revoke", json={"user_id": user["id"]})
        assert response.status_code == 200
        assert response.json() == {"detail": f"Tokens revoked for user {user['id']}"}


async def _login_and_set_cookies(client: httpx.AsyncClient, login_data: dict):
    """
    Helper function to log in a user and store access/refresh tokens in cookies.

    :param client: The async HTTP client.
    :param login_data: Dictionary containing user credentials.
    """
    response = await client.post("/api/auth/login", json=login_data)

    for token in ["access_token", "refresh_token"]:
        client.cookies.set(token, response.cookies.get(token))

    assert response.status_code == 200
    assert response.json() == {"detail": "Tokens set"}
