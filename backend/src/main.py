import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqladmin import Admin
from starlette.staticfiles import StaticFiles

from src.core.config import settings
from src.core.domain.exceptions import AppException

from src.core.presentation.middlewares import SecurityMiddleware, AuthenticationMiddleware, JWTRefreshMiddleware
from src.auth.presentation.api import auth_api_router
from src.auth.presentation.views import auth_view_router
from src.users.presentation.api import UserCRUDRouter, user_api_router
from src.users.presentation.admin import UserAdmin
from src.db.engine import engine
from src.db.utils import create_db_and_tables
from src.integrations.infrastructure.http.aiohttp_client import AiohttpClient
from src.vacancies.presentation.admin import VacancyAdmin
from src.vacancies.presentation.api import vacancy_api_router, VacancyCRUDRouter


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()  # Only needed if Alembic is not used
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


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            **(exc.kwargs or {})
        }
    )


# Middlewares are processed in reverse order
# JWTRefreshMiddleware -> AuthenticationMiddleware -> SecurityMiddleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(JWTRefreshMiddleware)

Instrumentator().instrument(app).expose(app, endpoint='/__internal_metrics__')

app.mount("/static", StaticFiles(directory="/static"), name="static")

app.include_router(auth_api_router, prefix='/api', tags=["auth"])
app.include_router(auth_view_router, prefix='/auth', tags=["auth"])
app.include_router(user_api_router, prefix='/api/users', tags=["users"])
app.include_router(UserCRUDRouter().get_router(), prefix='/api/crud-users', tags=["crud-users"])
app.include_router(vacancy_api_router, prefix='/api/vacancies', tags=["vacancies"])
app.include_router(VacancyCRUDRouter().get_router(), prefix='/api/crud-vacancies', tags=["crud-vacancies"])


admin = Admin(app, engine)
admin.add_view(UserAdmin)
admin.add_view(VacancyAdmin)
