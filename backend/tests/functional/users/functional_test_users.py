import httpx
import pytest

from src.users.presentation.dependencies import get_user_uow
from tests.utils import override_dependencies


@pytest.mark.asyncio
async def test_me(client: httpx.AsyncClient) -> None:
    """
    Test the /me endpoint for an anonymous user.

    Ensures that default anonymous user fields are returned.
    """
    response = await client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json() == {
        'id': None,
        'email': None,
        'is_active': False,
        'is_superuser': False,
        'is_verified': False
    }


@pytest.mark.asyncio
async def test_register(client: httpx.AsyncClient, fake_user_uow):
    """
    Test registering a new user via the public API.

    Verifies that the user is created and the response contains correct email.
    """
    async with override_dependencies({get_user_uow: lambda: fake_user_uow}):
        new_user_data = await create_user_via_api(client, "user@example.com")
        assert new_user_data["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_get_profile(client: httpx.AsyncClient, fake_user_uow):
    """
    Test retrieving a user profile by ID.

    Ensures that the correct user data is returned after registration.
    """
    async with override_dependencies({get_user_uow: lambda: fake_user_uow}):
        new_user_data = await create_user_via_api(client)

        response = await client.get(f"/api/users/{new_user_data["id"]}")
        data = response.json()
        assert response.status_code == 200
        assert data["email"] == new_user_data["email"]


@pytest.mark.asyncio
async def test_update_user(client: httpx.AsyncClient, fake_user_uow):
    """
    Test updating user email via PATCH request.

    Verifies that the user's email is updated and reflected in the response.
    """
    async with override_dependencies({get_user_uow: lambda: fake_user_uow}):
        new_user_data = await create_user_via_api(client)

        response = await client.patch(
            url=f"/api/users/{new_user_data["id"]}",
            json={"email": "user_new@example.com"},
        )
        updated_data = response.json()
        assert response.status_code == 200
        assert updated_data["email"] == "user_new@example.com"


@pytest.mark.asyncio
async def test_delete_user(client: httpx.AsyncClient, fake_user_uow):
    """
    Test deleting a user by ID.

    Ensures that the user is successfully deleted via the API.
    """
    async with override_dependencies({get_user_uow: lambda: fake_user_uow}):
        new_user_data = await create_user_via_api(client)

        response = await client.delete(f"/api/users/{new_user_data["id"]}")
        assert response.status_code == 200


async def create_user_via_api(client: httpx.AsyncClient, email: str = "user@example.com") -> dict:
    """
    Helper function to create a user via API for testing.

    Sends a POST request to /api/users and returns the response JSON.
    """
    response = await client.get(f"/api/users/{1}")
    assert response.status_code == 404

    response = await client.post(
        url="/api/users",
        json={
            "email": email,
            "password": "securepassword!1",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        },
    )
    assert response.status_code == 200
    return response.json()
