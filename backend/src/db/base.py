from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

DB_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    This class is used as a declarative base with custom metadata,
    including naming conventions for constraints and indexes.

    Attributes:
        metadata (MetaData): SQLAlchemy metadata object with naming conventions applied.
    """
    metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
