from datetime import timedelta
from typing import Any, Literal

from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from pydantic import SecretStr
from starlette.requests import Request
from starlette.responses import Response

from src.auth.config import auth_config
from src.auth.exceptions import RefreshTokenNotValid
from src.auth.schemas import JWTData, User
from src.auth.transport.cookie import CookieTransport
from src.utils.datetimes import get_timezone_now

SecretType = str | SecretStr
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/tokens", auto_error=False)


class JWT:
    """
    Класс для создания/чтения JWT токенов
    """

    def create_access_token(self, data: dict) -> str:
        """Создание access токена с установленными настройками через ENV"""
        return self._create_jwt(
            data=data,
            secret=auth_config.JWT_ACCESS_SECRET,
            lifetime_seconds=auth_config.ACCESS_TOKEN_EXPIRE_SECONDS,
        )

    def create_refresh_token(self, data: dict) -> str:
        """Создание refresh токена с установленными настройками через ENV"""
        return self._create_jwt(
            data=data,
            secret=auth_config.JWT_REFRESH_SECRET,
            lifetime_seconds=auth_config.REFRESH_TOKEN_EXPIRE_SECONDS,
        )

    def read_token(self, token: str | None, token_type: Literal['access', 'refresh']) -> JWTData | None:
        """Читаем JWT токен, проверяем есть ли данные о пользователе, возвращаем JWTData"""
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
            return JWTData(**data)
        except JWTError:
            return None

    def _create_jwt(
        self,
        data: dict,
        secret: SecretType,
        lifetime_seconds: int | None = None,
        algorithm: str = auth_config.JWT_ALGORITHM,
    ) -> str:
        """Создание JWT токена"""
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


class JWTAuth:
    """
    Класс для работы с авторизацией через cookie JWT,
    может быть использован как зависимость в routers.
    """
    def __init__(self, request: Request = None, response: Response = None):
        self.request = request
        self.response = response
        self._jwt = JWT()

    def set_tokens(self, user: User) -> None:
        """
        Установить JWT токены (access, refresh) в текущий response,
        который приходит вместе с запросом
        """
        data = {
            "user_id": str(user.id),
            "is_superuser": user.is_superuser,
        }
        access_token = self._jwt.create_access_token(data)
        refresh_token = self._jwt.create_refresh_token(data)
        self.set_access_token(access_token)
        self.set_refresh_token(refresh_token)

    def unset_tokens(self) -> None:
        """
        Удалить JWT токены
        """
        if auth_config.JWT_METHOD in ["cookies", "both"]:
            CookieTransport(cookie_name="access_token").delete_cookie(self.response)
            CookieTransport(cookie_name="refresh_token").delete_cookie(self.response)

        if auth_config.JWT_METHOD in ["headers", "both"]:
            self.response.headers[auth_config.JWT_ACCESS_HEADER_NAME] = ""
            self.response.headers[auth_config.JWT_REFRESH_HEADER_NAME] = ""

    def set_access_token(self, access_token: str,) -> None:
        """Установить access token в текущий response"""
        if auth_config.JWT_METHOD in ["cookies", "both"]:
            CookieTransport(
                cookie_name="access_token",
                cookie_max_age=auth_config.ACCESS_TOKEN_EXPIRE_SECONDS
            ).set_login_cookie(self.response, access_token)

        if auth_config.JWT_METHOD in ["headers", "both"]:
            self.response.headers[
                auth_config.JWT_ACCESS_HEADER_NAME
            ] = f"{auth_config.JWT_ACCESS_HEADER_TYPE} {access_token}"

    def set_refresh_token(self, refresh_token: str,) -> None:
        """Установить refresh token в текущий response"""
        if auth_config.JWT_METHOD in ["cookies", "both"]:
            CookieTransport(
                cookie_name="refresh_token",
                cookie_max_age=auth_config.REFRESH_TOKEN_EXPIRE_SECONDS,
            ).set_login_cookie(self.response, refresh_token)

        if auth_config.JWT_METHOD in ["headers", "both"]:
            self.response.headers[auth_config.JWT_REFRESH_HEADER_NAME] = refresh_token

    def refresh_access_token(self) -> None:
        """
        Обновить access токен через refresh, если тот есть
        """
        refresh_token_data = self.read_refresh_token()
        if not refresh_token_data:
            raise RefreshTokenNotValid()
        access_token = self._jwt.create_access_token(refresh_token_data.dict())
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

            if auth_config.JWT_METHOD in ["cookies", "both"]:
                access_cookie_transport = CookieTransport(
                    cookie_name="access_token",
                    cookie_max_age=auth_config.ACCESS_TOKEN_EXPIRE_SECONDS
                )
                access_cookie_transport.set_login_cookie(response, access_token)

            if auth_config.JWT_METHOD in ["headers", "both"]:
                response.headers[
                    auth_config.JWT_ACCESS_HEADER_NAME
                ] = f"{auth_config.JWT_ACCESS_HEADER_TYPE} {access_token}"

    def read_access_token(self) -> JWTData | None:
        """Получить данные по текущему access token'у"""
        token = self._get_access_token()
        return self._jwt.read_token(token, 'access')

    def read_refresh_token(self) -> JWTData | None:
        """Получить данные по текущему refresh token'у"""
        token = self._get_refresh_token()
        return self._jwt.read_token(token, 'refresh')

    def _get_access_token(self) -> str | None:
        """Получить текущий access token"""
        cookie_token = header_token = None
        if hasattr(self.request.state, "access_token"):
            return self.request.state.access_token

        if auth_config.JWT_METHOD in ["cookies", "both"]:
            cookie_token = self.request.cookies.get('access_token', None)

        if auth_config.JWT_METHOD in ["headers", "both"]:
            refresh_header = self.request.headers.get(auth_config.JWT_REFRESH_HEADER_NAME)
            if refresh_header:
                try:
                    header_token = refresh_header.split(" ")[1]
                except IndexError:
                    header_token = None
        return cookie_token or header_token

    def _get_refresh_token(self) -> str | None:
        """Получить текущий refresh token"""
        cookie_token = header_token = None
        if auth_config.JWT_METHOD in ["cookies", "both"]:
            cookie_token = self.request.cookies.get('refresh_token', None)

        if auth_config.JWT_METHOD in ["headers", "both"]:
            refresh_header = self.request.headers.get(auth_config.JWT_REFRESH_HEADER_NAME)
            if refresh_header:
                try:
                    header_token = refresh_header.split(" ")[1]
                except IndexError:
                    header_token = None
        return cookie_token or header_token


