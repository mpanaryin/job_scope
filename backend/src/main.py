import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqladmin import Admin
from starlette.staticfiles import StaticFiles

import src.core.logging_setup  # важно объявить до всех импортов
from src.core.config import settings

from src.core.middlewares import SecurityMiddleware, AuthenticationMiddleware, JWTRefreshMiddleware
from src.auth.api import api_router as auth_api_router
from src.auth.views import router as auth_view_router
from src.users.api import UserCRUDRouter
from src.users.admin import UserAdmin
from src.db.engine import engine
from src.db.utils import create_db_and_tables
from src.utils.aiohttp_client import AiohttpClient
from src.vacancies.admin import VacancyAdmin
from src.vacancies.api import router as vacancies_router, VacancyCRUDRouter


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()  # Нужен только если нет alembic
    yield



async def on_startup():
    AiohttpClient.get_aiohttp_client()


async def on_shutdown():
    await AiohttpClient.close_aiohttp_client()


app = FastAPI(
    title=settings.PROJECT_NAME,
    on_startup=[on_startup],
    on_shutdown=[on_shutdown]
)  # lifespan если нет alembic

# Middleware обрабатываются в обратном порядке
# JWTRefreshMiddleware -> AuthenticationMiddleware -> SecurityMiddleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(JWTRefreshMiddleware)
Instrumentator().instrument(app).expose(app, endpoint='/__internal_metrics__')

app.mount("/static", StaticFiles(directory="/static"), name="static")

app.include_router(auth_api_router, prefix='/api', tags=["auth"])
app.include_router(auth_view_router, prefix='/auth', tags=["auth"])
app.include_router(UserCRUDRouter().get_router(), prefix='/api/users', tags=["users"])
app.include_router(vacancies_router, prefix='/api/vacancies', tags=["vacancies"])
app.include_router(VacancyCRUDRouter().get_router(), prefix='/api/vacancies', tags=["vacancies"])

admin = Admin(app, engine)
admin.add_view(UserAdmin)
admin.add_view(VacancyAdmin)
