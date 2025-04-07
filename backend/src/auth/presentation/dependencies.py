from typing import Annotated

from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response

from src.auth.config import auth_config
from src.auth.domain.entities import TokenType
from src.auth.infrastructure.services.jwt import JWTAuth, JWTProvider
from src.auth.infrastructure.services.redis_token_storage import RedisTokenStorageService
from src.auth.infrastructure.transport.cookie import CookieTransport
from src.auth.infrastructure.transport.header import HeaderTransport


def get_redis_token_storage() -> RedisTokenStorageService:
    """Получить Redis хранилище для токенов"""
    return RedisTokenStorageService()


async def get_jwt_auth(request: Request = None, response: Response = None) -> JWTAuth:
    """Получить сервис авторизации по JWT с текущими настройками AuthConfig"""
    jwt_provider = JWTProvider()

    access_transports = []
    refresh_transports = []
    if auth_config.JWT_METHOD in ['cookie', 'all']:
        access_transports.append(
            CookieTransport(cookie_name="access_token", cookie_max_age=auth_config.ACCESS_TOKEN_EXPIRE_SECONDS)
        )
        refresh_transports.append(
            CookieTransport(cookie_name="refresh_token", cookie_max_age=auth_config.REFRESH_TOKEN_EXPIRE_SECONDS)
        )
    if auth_config.JWT_METHOD in ['header', 'all']:
        access_transports.append(HeaderTransport(auth_config.JWT_ACCESS_HEADER_NAME, auth_config.JWT_HEADER_TYPE))
        refresh_transports.append(HeaderTransport(auth_config.JWT_REFRESH_HEADER_NAME, auth_config.JWT_HEADER_TYPE))

    transports = {
        TokenType.ACCESS: access_transports,
        TokenType.REFRESH: refresh_transports
    }

    return JWTAuth(jwt_provider, transports, get_redis_token_storage(), request=request, response=response)

JWTAuthDep = Annotated[JWTAuth, Depends(get_jwt_auth)]
