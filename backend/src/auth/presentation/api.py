from fastapi import APIRouter
from starlette.requests import Request

from src.auth.application.use_cases.authenticate import authenticate
from src.auth.presentation.dependencies import JWTAuthDep
from src.auth.presentation.permissions import access_control
from src.auth.domain.entities import AuthUser
from src.users.domain.dtos import UserReadDTO
from src.users.infrastructure.db.unit_of_work import PGUserUnitOfWork

auth_api_router = APIRouter()


@auth_api_router.post("/users/login")
async def login(credentials: AuthUser, auth: JWTAuthDep):
    """Вход в аккаунт"""
    await authenticate(credentials, PGUserUnitOfWork(), auth)
    return {"msg": "Tokens set"}


@auth_api_router.post("/users/logout")
async def logout(auth: JWTAuthDep):
    """Выход из аккаунта"""
    auth.unset_tokens()
    return {"msg": "Tokens deleted"}


@auth_api_router.post("/users/refresh")
async def refresh(auth: JWTAuthDep):
    """Выход из аккаунта"""
    auth.refresh_access_token()
    return {"msg": "The token has been refresh"}


@auth_api_router.get("/users/me")
@access_control(open=True)
async def get_my_account(request: Request) -> UserReadDTO:
    """Получаем свой профиль, если мы авторизованы"""
    return request.state.user
