from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from sqladmin import Admin
from starlette.staticfiles import StaticFiles

from src.core.middlewares import SecurityMiddleware, AuthenticationMiddleware, JWTRefreshMiddleware
from src.auth.api import api_router as auth_api_router
from src.auth.views import router as auth_view_router
from src.users.api import UserCRUDRouter
from src.users.admin import UserAdmin
from src.db.engine import engine
from src.db.utils import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Нужен только если нет alembic
    await create_db_and_tables()
    yield


app = FastAPI()  # lifespan если нет alembic
# Middleware обрабатываются в обратном порядке
# JWTRefreshMiddleware -> AuthenticationMiddleware -> SecurityMiddleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(JWTRefreshMiddleware)

admin = Admin(app, engine)
app.mount('/src/static', StaticFiles(directory='src/static'), name='static')

app.include_router(auth_api_router, prefix='/api', tags=["auth"])
app.include_router(auth_view_router, prefix='/auth', tags=["auth"])
app.include_router(UserCRUDRouter().get_router(), prefix='/api/users', tags=["users"])

admin.add_view(UserAdmin)
