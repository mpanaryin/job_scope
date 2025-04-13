from unittest.mock import MagicMock, AsyncMock

import pytest

from src.auth.application.use_cases.authentication import authenticate
from src.auth.domain.dtos import AuthUserDTO
from src.users.domain.entities import UserCreate
from tests.fakes.users import FakeUserUnitOfWork


@pytest.mark.asyncio
async def test_authenticate(monkeypatch):
    # Arrange
    uow = FakeUserUnitOfWork()
    user_data = UserCreate(
        email="user@example.com",
        hashed_password="securepassword!1_hashed",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    user = await uow.users.add(user_data)

    # Подменим check_password
    monkeypatch.setattr(
        "src.auth.application.use_cases.authentication.check_password",
        lambda password, hashed: True
    )

    # Подготовим mock auth
    mock_auth = MagicMock()
    mock_auth.set_tokens = AsyncMock()

    # Act
    result = await authenticate(
        credentials=AuthUserDTO(email="user@example.com", password="securepassword!1"),
        uow=uow,
        auth=mock_auth
    )

    # Assert
    assert result.email == user.email
    mock_auth.set_tokens.assert_awaited_once_with(result)
