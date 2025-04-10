import pytest

from src.users.application.use_cases.user_registration import register_user
from src.users.application.use_cases.user_profile import get_user_profile
from src.users.application.use_cases.user_update import update_user
from src.users.application.use_cases.user_delete import delete_user
from src.users.domain.dtos import UserCreateDTO, UserUpdateDTO
from src.users.domain.exceptions import UserNotFound


@pytest.mark.asyncio
async def test_register_user(fake_uow, monkeypatch):
    # Подготовка данных
    create_data = UserCreateDTO(
        email="user@example.com",
        password="securepassword!1",
        is_active=True,
        is_superuser=False,
        is_verified=False
    )
    # Выполнение use case
    user = await register_user(create_data, fake_uow)

    assert user.email == create_data.email


@pytest.mark.asyncio
async def test_get_user_profile(fake_uow):
    # Подготовка данных
    create_data = UserCreateDTO(
        email="user@example.com",
        password="securepassword!1",
        is_active=True,
        is_superuser=False,
        is_verified=False
    )
    # Выполнение use case
    user = await register_user(create_data, fake_uow)
    result = await get_user_profile(user_pk=user.id, uow=fake_uow)
    assert result.id == 1
    assert result.email == "user@example.com"

    with pytest.raises(UserNotFound) as exc:
        await get_user_profile(user_pk=-1, uow=fake_uow)
    assert exc.type is UserNotFound


@pytest.mark.asyncio
async def test_update_user(fake_uow):
    # Подготовка данных
    create_data = UserCreateDTO(
        email="user@example.com",
        password="securepassword!1",
        is_active=True,
        is_superuser=False,
        is_verified=False
    )
    update_data = UserUpdateDTO(email="user_new@example.com")
    # Выполнение use case
    user = await register_user(create_data, fake_uow)
    new_user = await update_user(user_pk=user.id, user_data=update_data, uow=fake_uow)
    assert new_user.id == user.id
    assert new_user.email == "user_new@example.com"

    with pytest.raises(UserNotFound) as exc:
        await update_user(user_pk=-1, user_data=update_data, uow=fake_uow)
    assert exc.type is UserNotFound


@pytest.mark.asyncio
async def test_delete_user(fake_uow):
    # Подготовка данных
    create_data = UserCreateDTO(
        email="user@example.com",
        password="securepassword!1",
        is_active=True,
        is_superuser=False,
        is_verified=False
    )
    # Выполнение use case
    user = await register_user(create_data, fake_uow)
    no_user = await delete_user(user_pk=user.id, uow=fake_uow)
    assert no_user is None

    with pytest.raises(UserNotFound) as exc:
        await delete_user(user_pk=user.id, uow=fake_uow)
    assert exc.type is UserNotFound
