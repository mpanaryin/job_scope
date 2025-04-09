from src.core.domain.entities import CustomModel


class User(CustomModel):
    """
    Domain model representing a user in the system.

    This entity encapsulates the core business attributes of a user,
    independent of how they are persisted or exposed externally.

    Attributes:
        id: Unique identifier of the user.
        email: Email address associated with the user.
        hashed_password: Hashed password for authentication.
        is_active: Indicates whether the user is currently active.
        is_superuser: Indicates whether the user has administrative privileges.
        is_verified: Indicates whether the user has verified their email address.
    """
    id: int
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(CustomModel):
    """
    Domain model representing user data required for creation.

    Used to encapsulate the input necessary to create a new user in the system.

    Attributes:
        email: Email address of the new user.
        hashed_password: Secure hashed password.
        is_active: Whether the new user should be active.
        is_superuser: Whether the user has elevated privileges.
        is_verified: Whether the user's email is verified.
    """
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserUpdate(CustomModel):
    """
    Domain model for updating user information.

    Represents a partial update operation for a user entity.

    Attributes:
        id: ID of the user to be updated.
        email: New email address (optional).
        is_active: Whether the user should be active (optional).
        is_superuser: Whether the user should be a superuser (optional).
        is_verified: Whether the user is verified (optional).
    """
    id: int
    email: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False
