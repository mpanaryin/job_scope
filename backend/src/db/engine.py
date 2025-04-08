from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings


# Database connection URL loaded from environment/config
DATABASE_URL = settings.DATABASE_URI

# Asynchronous SQLAlchemy engine
engine = create_async_engine(DATABASE_URL)

# Asynchronous session factory for database operations
# `expire_on_commit=False` keeps objects alive after commit
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
