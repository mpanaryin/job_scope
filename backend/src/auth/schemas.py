import re

from fastapi import Form
from pydantic import EmailStr, Field, field_validator

from src.core.constants import STRONG_PASSWORD_PATTERN
from src.core.schemas import CustomModel


class AuthUser(CustomModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    @classmethod
    def as_form(
        cls,
        email: EmailStr = Form(...),
        password: str = Form(..., min_length=6, max_length=128),
    ):
        return cls(email=email, password=password)


class AuthUserForm(CustomModel):
    email: EmailStr | None = Form(...)
    password: EmailStr | None = Form(...)

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


class JWTData(CustomModel):
    user_id: int = Field(alias="user_id")
    is_superuser: bool = False
    exp: int


class AnonymousUser(CustomModel):
    id: int = None
    email: str = None
    hashed_password: str = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
