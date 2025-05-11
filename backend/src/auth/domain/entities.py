import datetime
from enum import Enum

from src.core.domain.entities import CustomModel


class TokenType(str, Enum):
    """
    Defines the type of token used for authentication.
    """
    ACCESS = "access"
    REFRESH = "refresh"


class TokenData(CustomModel):
    """
    Represents the decoded token payload.

    Used internally after decoding and validating a token, or
    for generating a new one with specific claims.
    """
    user_id: int
    is_superuser: bool = False
    exp: datetime.datetime
    jti: str | None = None
    aud: str | None = None
    iss: str | None = None


class AnonymousUser(CustomModel):
    """
    Represents a guest or unauthenticated user.
    """
    id: None = None
    email: None = None
    hashed_password: None = None
    is_active: bool = False
    is_superuser: bool = False
    is_verified: bool = False

    def __bool__(self) -> bool:
        """
        Usage:
        if not user:
            `some actions`
        """
        return False
