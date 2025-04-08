from fastapi import Form
from pydantic import EmailStr, Field

from src.core.domain.entities import CustomModel


class AuthUserDTO(CustomModel):
    """
    Represents credentials submitted during login or registration.
    """
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    @classmethod
    def as_form(
        cls,
        email: EmailStr = Form(...),
        password: str = Form(..., min_length=6, max_length=128),
    ):
        return cls(email=email, password=password)
