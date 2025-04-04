from src.users.services import UserService
from src.core.config import settings
from src.db.base import Base
from src.db.engine import engine
# Тут импорты всех моделей, которые должны создаваться при create_db_and_tables
from src.users.orm import User
from src.vacancies.infrastructure.db.orm import Vacancy


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await create_superuser(settings.FIRST_SUPERUSER, settings.FIRST_SUPERUSER_PASSWORD)


async def create_superuser(email: str, password: str):
    superuser = await UserService().get_by_email(email)
    if not superuser:
        superuser = await UserService().create(
            data={'email': email, 'password': password, 'is_active': True, 'is_superuser': True},
        )
        print('User created!')
    return superuser
