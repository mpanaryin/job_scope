import re

from pydantic import Field, field_validator

from src.core.domain.constants import STRONG_PASSWORD_PATTERN
from src.core.domain.entities import CustomModel
from src.users.domain.entities import UserUpdate


class UserReadDTO(CustomModel):
    """
    Data Transfer Object for user output.

    This model is designed to represent both authenticated and anonymous users,
    allowing unified usage in views like `/users/me`.

    Attributes:
        id: User ID (optional for anonymous users).
        email: Email address of the user.
        is_active: Whether the user account is active.
        is_superuser: Whether the user has administrative privileges.
        is_verified: Whether the user has verified their email.
    """
    id: int | None
    email: str | None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreateDTO(CustomModel):
    """
    Data Transfer Object for user creation.

    This model is used when registering a new user.
    It includes password validation and default flags for user status.

    Attributes:
        email: User email address.
        password: Raw password (must meet strong password requirements).
        is_active: Whether the user account is active.
        is_superuser: Whether the user has administrative privileges.
        is_verified: Whether the user's email is verified.
    """
    email: str
    password: str = Field(min_length=6, max_length=128)
    is_active: bool | None = False
    is_superuser: bool | None = False
    is_verified: bool | None = False

    @field_validator("password", mode="after")
    def valid_password(cls, password: str) -> str:
        """
        Validate password strength.

        Ensures the password contains at least one lowercase letter,
        one uppercase letter, one digit or special character.

        :param password: Raw user password.
        :return: Validated password.
        :raises ValueError: If password does not match the required pattern.
        """
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit or special symbol"
            )

        return password


class UserUpdateDTO(CustomModel):
    """
    Data Transfer Object for updating user information.

    This model is used in endpoints for partial updates to user data.

    Attributes:
        email: Updated email address (optional).
        is_active: Whether the user account is active.
        is_superuser: Whether the user has administrative privileges.
        is_verified: Whether the user has verified their email.
    """
    email: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False

    def to_entity(self, user_id: int):
        return UserUpdate(id=user_id, **self.model_dump(exclude_unset=True))
