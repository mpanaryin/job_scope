from unittest.mock import MagicMock, AsyncMock

import pytest

from src.auth.application.use_cases.authentication import authenticate
from src.auth.presentation.dtos import AuthUserDTO
from src.users.domain.entities import UserCreate
from src.users.domain.interfaces.user_uow import IUserUnitOfWork


@pytest.mark.asyncio
async def test_authenticate(monkeypatch, fake_user_uow: IUserUnitOfWork):
    """
    Test successful user authentication.

    Verifies that a valid user with correct credentials is authenticated
    and that tokens are set via the auth service.
    """
    # Arrange
    user_data = UserCreate(
        email="user@example.com",
        hashed_password="securepassword!1_hashed",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    user = await fake_user_uow.users.add(user_data)

    mock_hasher = MagicMock()
    mock_hasher.hash = MagicMock()
    mock_hasher.hash.return_value = True

    mock_auth = MagicMock()
    mock_auth.set_tokens = AsyncMock()

    auth_dto = AuthUserDTO(email=user_data.email, password="securepassword!1")
    # Act
    result = await authenticate(
        email=auth_dto.email,
        password=auth_dto.password,
        pwd_hasher=mock_hasher,
        uow=fake_user_uow,
        auth=mock_auth
    )
    # Assert
    assert result.email == user.email
    mock_auth.set_tokens.assert_awaited_once_with(result)
