import pytest
import httpx

from src.users.domain.dtos import UserCreateDTO

new_user = UserCreateDTO(
    email="new_user@email.com",
    password="Securepassword!1",
    is_active=True, is_verified=True, is_superuser=False
)


@pytest.mark.asyncio(loop_scope="session")
async def test_register_and_get_profile(clear_db, user_factory):
    """
    Test registering a user and retrieving their profile.

    Verifies that the user is created successfully and the profile
    endpoint returns correct data for the given user ID.
    """
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        user = await user_factory(client=client, user=new_user)
        assert user["email"] == new_user.email

        response = await client.get(f"/api/users/{user["id"]}")
        assert response.status_code == 200
        profile = response.json()
        assert profile["email"] == new_user.email


@pytest.mark.asyncio(loop_scope="session")
async def test_register_and_update_user(clear_db, user_factory):
    """
    Test registering a user and updating their email.

    Verifies that the PATCH request updates the user's email and
    the response reflects the changes.
    """
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        user = await user_factory(client=client, user=new_user)
        assert user["email"] == new_user.email

        new_email = "updated_user@email.com"
        response = await client.patch(f"/api/users/{user["id"]}", json={
            "email": new_email
        })
        assert response.status_code == 200
        updated_data = response.json()
        assert updated_data["email"] == new_email


@pytest.mark.asyncio(loop_scope="session")
async def test_register_and_delete_user(clear_db, user_factory):
    """
    Test registering and then deleting a user.

    Ensures that the DELETE endpoint successfully removes the user.
    """
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        user = await user_factory(client=client, user=new_user)
        assert user["email"] == new_user.email

        response = await client.delete(f"/api/users/{user["id"]}")
        assert response.status_code == 200
