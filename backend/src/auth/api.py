from fastapi import APIRouter
from starlette.requests import Request

from src.auth.dependencies import JWTAuthDep
from src.auth.permissions import access_control
from src.auth.schemas import AuthUser
from src.auth.services import authenticate
from src.users.schemas import User

api_router = APIRouter()


@api_router.post("/users/login")
async def login(credentials: AuthUser, auth: JWTAuthDep):
    """Вход в аккаунт"""
    user = await authenticate(credentials)
    auth.set_tokens(user)
    return {"msg": "Tokens set"}


@api_router.post("/users/logout")
async def logout(auth: JWTAuthDep):
    """Выход из аккаунта"""
    auth.unset_tokens()
    return {"msg": "Tokens deleted"}


@api_router.post("/users/refresh")
async def refresh(auth: JWTAuthDep):
    """Выход из аккаунта"""
    auth.refresh_access_token()
    return {"msg": "The token has been refresh"}


@api_router.get("/users/me")
@access_control(open=True)
async def get_my_account(request: Request) -> User:
    """Получаем свой профиль, если мы авторизованы"""
    return request.state.user
