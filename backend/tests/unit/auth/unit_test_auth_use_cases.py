from unittest.mock import MagicMock, AsyncMock

import pytest

from src.auth.application.use_cases.authentication import authenticate
from src.auth.domain.dtos import AuthUserDTO
from src.users.domain.entities import UserCreate
from src.users.domain.interfaces import IUserUnitOfWork


@pytest.mark.asyncio
async def test_authenticate(monkeypatch, fake_user_uow: IUserUnitOfWork):
    # Arrange
    user_data = UserCreate(
        email="user@example.com",
        hashed_password="securepassword!1_hashed",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    user = await fake_user_uow.users.add(user_data)

    monkeypatch.setattr(
        "src.auth.application.use_cases.authentication.check_password",
        lambda password, hashed: True
    )

    mock_auth = MagicMock()
    mock_auth.set_tokens = AsyncMock()
    # Act
    result = await authenticate(
        credentials=AuthUserDTO(email=user_data.email, password="securepassword!1"),
        uow=fake_user_uow,
        auth=mock_auth
    )
    # Assert
    assert result.email == user.email
    mock_auth.set_tokens.assert_awaited_once_with(result)
