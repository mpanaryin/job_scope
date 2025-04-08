import re

from pydantic import Field, field_validator

from src.core.domain.constants import STRONG_PASSWORD_PATTERN
from src.core.domain.entities import CustomModel


class UserReadDTO(CustomModel):
    """
    Data Transfer Object for user output.

    This model is designed to represent both authenticated and anonymous users,
    allowing unified usage in views like `/users/me`.
    """
    id: int | None
    email: str | None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreateDTO(CustomModel):
    email: str
    password: str = Field(min_length=6, max_length=128)
    is_active: bool | None = False
    is_superuser: bool | None = False
    is_verified: bool | None = False

    @field_validator("password", mode="after")
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit or "
                "special symbol"
            )

        return password


class UserUpdateDTO(CustomModel):
    email: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False

