from datetime import timedelta
from typing import Any, Literal
from jose import jwt, JWTError
from pydantic import SecretStr
from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.entities import TokenData, TokenType
from src.auth.domain.interfaces import ITokenProvider, ITokenAuth
from src.auth.config import auth_config
from src.auth.domain.exceptions import RefreshTokenNotValid
from src.auth.infrastructure.transport.base import IAuthTransport
from src.users.domain.entities import User
from src.utils.datetimes import get_timezone_now

SecretType = str | SecretStr


class JWTProvider(ITokenProvider):
    """
    Сервис для создания/чтения JWT токенов.
    """

    def create_access_token(self, data: dict) -> str:
        """Создание access токена с установленными настройками через ENV"""
        return self._encode_jwt(
            data=data,
            secret=auth_config.JWT_ACCESS_SECRET,
            lifetime_seconds=auth_config.ACCESS_TOKEN_EXPIRE_SECONDS,
        )

    def create_refresh_token(self, data: dict) -> str:
        """Создание refresh токена с установленными настройками через ENV"""
        return self._encode_jwt(
            data=data,
            secret=auth_config.JWT_REFRESH_SECRET,
            lifetime_seconds=auth_config.REFRESH_TOKEN_EXPIRE_SECONDS,
        )

    def read_token(self, token: str | None, token_type: Literal['access', 'refresh']) -> TokenData | None:
        """Читаем JWT токен, проверяем есть ли данные о пользователе, возвращаем TokenData"""
        if token is None:
            return None

        if token_type == 'access':
            secret = auth_config.JWT_ACCESS_SECRET
        else:
            secret = auth_config.JWT_REFRESH_SECRET

        try:
            data = self._decode_jwt(token, secret, algorithms=[auth_config.JWT_ALGORITHM])
            user_id = data.get("user_id")
            if user_id is None:
                return None
            return TokenData(**data)
        except JWTError:
            return None

    def _encode_jwt(
        self,
        data: dict,
        secret: SecretType,
        lifetime_seconds: int | None = None,
        algorithm: str = auth_config.JWT_ALGORITHM,
    ) -> str:
        """Кодирование JWT токена"""
        payload = data.copy()
        if lifetime_seconds:
            expire = get_timezone_now() + timedelta(seconds=lifetime_seconds)
            payload["exp"] = expire
        return jwt.encode(payload, self._get_secret_value(secret), algorithm=algorithm)

    def _decode_jwt(
        self,
        encoded_jwt: str,
        secret: SecretType,
        algorithms: list[str] | None = None,
    ) -> dict[str, Any]:
        """Декодирование JWT Токена"""
        if algorithms is None:
            algorithms = [auth_config.JWT_ALGORITHM]
        return jwt.decode(
            encoded_jwt,
            self._get_secret_value(secret),
            algorithms=algorithms,
        )

    def _get_secret_value(self, secret: SecretType) -> str:
        if isinstance(secret, SecretStr):
            return secret.get_secret_value()
        return secret


class JWTAuth(ITokenAuth):
    def __init__(
        self,
        token_provider: ITokenProvider,
        transports: dict[TokenType, list[IAuthTransport]],
        request: Request = None,
        response: Response = None
    ):
        super().__init__(token_provider)
        self.transports = transports
        self.request = request
        self.response = response

    def set_tokens(self, user: User) -> None:
        """
        Установить JWT токены (access, refresh) в текущий response,
        который приходит вместе с запросом
        """
        data = {
            "user_id": str(user.id),
            "is_superuser": user.is_superuser,
        }
        access_token = self.token_provider.create_access_token(data)
        refresh_token = self.token_provider.create_refresh_token(data)
        self.set_access_token(access_token)
        self.set_refresh_token(refresh_token)

    def unset_tokens(self) -> None:
        """
        Удалить JWT токены
        """
        for token_type, transports in self.transports.items():
            for transport in transports:
                transport.delete_token(self.response)

        # if auth_config.JWT_METHOD in ["cookies", "both"]:
        #     CookieTransport(cookie_name="access_token").delete_token(self.response)
        #     CookieTransport(cookie_name="refresh_token").delete_token(self.response)
        #
        # if auth_config.JWT_METHOD in ["headers", "both"]:
        #     HeaderTransport(auth_config.JWT_ACCESS_HEADER_NAME).delete_token(self.response)
        #     HeaderTransport(auth_config.JWT_REFRESH_HEADER_NAME).delete_token(self.response)

    def set_access_token(self, access_token: str) -> None:
        """Установить access token в текущий response"""
        for token_type, transports in self.transports.items():
            if token_type == TokenType.ACCESS:
                for transport in transports:
                    transport.set_token(self.response, access_token)
        # if auth_config.JWT_METHOD in ["cookies", "both"]:
        #     CookieTransport(
        #         cookie_name="access_token", cookie_max_age=auth_config.ACCESS_TOKEN_EXPIRE_SECONDS
        #     ).set_token(self.response, access_token)
        #
        # if auth_config.JWT_METHOD in ["headers", "both"]:
        #     HeaderTransport(
        #         auth_config.JWT_ACCESS_HEADER_NAME, auth_config.JWT_HEADER_TYPE
        #     ).set_token(self.response, access_token)

    def set_refresh_token(self, refresh_token: str) -> None:
        """Установить refresh token в текущий response"""
        for token_type, transports in self.transports.items():
            if token_type == TokenType.REFRESH:
                for transport in transports:
                    transport.set_token(self.response, refresh_token)

        # if auth_config.JWT_METHOD in ["cookies", "both"]:
        #     CookieTransport(
        #         cookie_name="refresh_token", cookie_max_age=auth_config.REFRESH_TOKEN_EXPIRE_SECONDS
        #     ).set_token(self.response, refresh_token)
        #
        # if auth_config.JWT_METHOD in ["headers", "both"]:
        #     HeaderTransport(
        #         auth_config.JWT_REFRESH_HEADER_NAME, auth_config.JWT_HEADER_TYPE
        #     ).set_token(self.response, refresh_token)

    def refresh_access_token(self) -> None:
        """
        Обновить access токен через refresh, если тот есть
        """
        refresh_token_data = self.read_refresh_token()
        if not refresh_token_data:
            raise RefreshTokenNotValid()
        access_token = self.token_provider.create_access_token(refresh_token_data.dict())
        self.request.state.access_token = access_token
        # Так как у нас автообновление через middleware, то это лишняя работа.
        # Она полезна только при обновлении напрямую через endpoint
        if self.response:
            self.set_access_token(access_token)

    def update_response(self, response: Response):
        """
        Добавляет обновлённый токен в response
        Нужен для middleware
        """
        if hasattr(self.request.state, "access_token"):
            access_token = self.request.state.access_token
            self.response = response

            self.set_access_token(access_token)

    def read_access_token(self) -> TokenData | None:
        """Получить данные по текущему access token'у"""
        token = self._get_access_token()
        return self.token_provider.read_token(token, 'access')

    def read_refresh_token(self) -> TokenData | None:
        """Получить данные по текущему refresh token'у"""
        token = self._get_refresh_token()
        return self.token_provider.read_token(token, 'refresh')

    def _get_access_token(self) -> str | None:
        """Получить текущий access token"""
        cookie_token = header_token = None
        if hasattr(self.request.state, "access_token"):
            return self.request.state.access_token

        for token_type, transports in self.transports.items():
            if token_type == TokenType.ACCESS:
                for transport in transports:
                    token = transport.get_token(self.request)
                    if token is not None:
                        return token

        # if auth_config.JWT_METHOD in ["cookies", "both"]:
        #     cookie_token = self.request.cookies.get('access_token', None)
        #
        # if auth_config.JWT_METHOD in ["headers", "both"]:
        #     header_token = self.request.headers.get('access_token', None)
        #     if header_token:
        #         try:
        #             header_token = header_token.split(" ")[1]
        #         except IndexError:
        #             header_token = None
        return cookie_token or header_token

    def _get_refresh_token(self) -> str | None:
        """Получить текущий refresh token"""
        for token_type, transports in self.transports.items():
            if token_type == TokenType.REFRESH:
                for transport in transports:
                    token = transport.get_token(self.request)
                    if token is not None:
                        return token

        # cookie_token = header_token = None
        # if auth_config.JWT_METHOD in ["cookies", "both"]:
        #     cookie_token = self.request.cookies.get('refresh_token', None)
        #
        # if auth_config.JWT_METHOD in ["headers", "both"]:
        #     refresh_header = self.request.headers.get(auth_config.JWT_REFRESH_HEADER_NAME)
        #     if refresh_header:
        #         try:
        #             header_token = refresh_header.split(" ")[1]
        #         except IndexError:
        #             header_token = None
        # return cookie_token or header_token
