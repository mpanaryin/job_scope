from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

from src.core.domain.constants import DB_NAMING_CONVENTION


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    This class is used as a declarative base with custom metadata,
    including naming conventions for constraints and indexes.

    Attributes:
        metadata (MetaData): SQLAlchemy metadata object with naming conventions applied.
    """
    metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
