
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from src.core.config import settings
from src.db.base import Base
# Import models required for database initialization
from src.users.infrastructure.db.orm import UserDB
from src.vacancies.infrastructure.db.orm import Vacancy

config = context.config
fileConfig(config.config_file_name)

# Используем DeclarativeBase
target_metadata = Base.metadata


def get_url():
    return str(settings.ALEMBIC_DATABASE_URI)


def run_migrations_offline():
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=get_url()
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
