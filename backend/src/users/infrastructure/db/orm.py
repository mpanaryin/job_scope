from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class UserDB(Base):
    """
    SQLAlchemy ORM model representing a user entity in the database.

    Attributes:
        id (int): Primary key identifier of the user.
        email (str): Unique email address of the user.
        hashed_password (str): Securely hashed password.
        is_active (bool): Indicates whether the user account is active.
        is_superuser (bool): Indicates whether the user has administrative privileges.
        is_verified (bool): Indicates whether the user's email has been verified.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
