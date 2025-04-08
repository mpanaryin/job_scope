from src.users.infrastructure.db.crud import UserService
from src.db.base import Base
from src.db.engine import engine
# Import models required for database initialization
from src.users.infrastructure.db.orm import UserDB
from src.vacancies.infrastructure.db.orm import Vacancy


async def create_db_and_tables():
    """
    Create all database tables and initialize a superuser.

    This function should be called at application startup or for
    initial setup to ensure all models are created
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_superuser(email: str, password: str):
    """
    Create a superuser if it doesn't already exist.

    :param email: Email for the superuser.
    :param password: Plain-text password for the superuser.
    :return: The created or existing superuser instance.
    """
    superuser = await UserService().get_by_email(email)
    if not superuser:
        superuser = await UserService().create(
            data={'email': email, 'password': password, 'is_active': True, 'is_superuser': True},
        )
        print('User created!')
    return superuser
