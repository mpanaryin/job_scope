from fastapi import APIRouter, Depends
from starlette.requests import Request

from src.auth.application.use_cases.authentication import authenticate
from src.auth.presentation.dependencies import JWTAuthDep, get_redis_token_storage
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
    await auth.unset_tokens()
    return {"msg": "Tokens deleted"}


@auth_api_router.post("/users/refresh")
async def refresh(auth: JWTAuthDep):
    """Выход из аккаунта"""
    await auth.refresh_access_token()
    return {"msg": "The token has been refresh"}


@auth_api_router.post("/users/revoke_tokens/{user_id}")
async def revoke_tokens(user_id: str, token_storage=Depends(get_redis_token_storage)):
    """Отозвать токены пользователя"""
    await token_storage.revoke_tokens_by_user(user_id)
    return {"msg": f"Tokens revoked for user {user_id}"}


@auth_api_router.get("/users/me")
@access_control(open=True)
async def get_my_account(request: Request) -> UserReadDTO:
    """Получаем свой профиль, если мы авторизованы"""
    return request.state.user
