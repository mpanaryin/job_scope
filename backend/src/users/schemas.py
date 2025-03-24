import re

from pydantic import Field, field_validator

from src.core.constants import STRONG_PASSWORD_PATTERN
from src.core.schemas import CustomModel


class User(CustomModel):
    id: int
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(CustomModel):
    email: str
    password: str = Field(min_length=6, max_length=128)
    is_active: bool
    is_superuser: bool
    is_verified: bool

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


class UserUpdate(CustomModel):
    email: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False

