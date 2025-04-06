from enum import Enum

from fastapi import Form
from pydantic import EmailStr, Field

from src.core.schemas import CustomModel


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenData(CustomModel):
    user_id: int
    is_superuser: bool = False
    exp: int


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


class AnonymousUser(CustomModel):
    id: None = None
    email: None = None
    hashed_password: None = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
