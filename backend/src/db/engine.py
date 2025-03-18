from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings

DATABASE_URL = settings.DATABASE_URI  # settings.POSTGRES_DB_URI  # "sqlite+aiosqlite:///./test.db"


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
