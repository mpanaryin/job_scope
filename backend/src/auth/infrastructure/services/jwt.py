import uuid6
from datetime import timedelta
from typing import Any
from jose import jwt, JWTError
from pydantic import SecretStr
from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.entities import TokenData, TokenType
from src.auth.domain.interfaces import ITokenProvider, ITokenAuth, ITokenStorageService
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
            secret=auth_config.JWT_PRIVATE_KEY,
            lifetime_seconds=auth_config.ACCESS_TOKEN_EXPIRE_SECONDS,
        )

    def create_refresh_token(self, data: dict) -> str:
        """Создание refresh токена с установленными настройками через ENV"""
        return self._encode_jwt(
            data=data,
            secret=auth_config.JWT_PRIVATE_KEY,
            lifetime_seconds=auth_config.REFRESH_TOKEN_EXPIRE_SECONDS,
        )

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
        payload.setdefault("jti", str(uuid6.uuid6()))  # JWT ID
        payload.setdefault("iss", auth_config.JWT_ISSUER)
        return jwt.encode(payload, self._get_secret_value(secret), algorithm=algorithm)

    def read_token(self, token: str | None) -> TokenData | None:
        """Читаем JWT токен, проверяем есть ли данные о пользователе, возвращаем TokenData"""
        if token is None:
            return None

        try:
            data = self._decode_jwt(token, auth_config.JWT_PUBLIC_KEY, algorithms=[auth_config.JWT_ALGORITHM])
            user_id = data.get("user_id")
            if user_id is None:
                return None
            return TokenData(**data)
        except JWTError as e:
            return None

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
            token=encoded_jwt,
            key=self._get_secret_value(secret),
            algorithms=algorithms,
            issuer=auth_config.JWT_ISSUER
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
        token_storage: ITokenStorageService = None,
        request: Request = None,
        response: Response = None
    ):
        super().__init__(token_provider)
        self.token_storage = token_storage
        self.transports = transports
        self.request = request
        self.response = response

    async def set_tokens(self, user: User) -> None:
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
        await self.set_token(access_token, TokenType.ACCESS)
        await self.set_token(refresh_token, TokenType.REFRESH)

    async def unset_tokens(self) -> None:
        """
        Удалить JWT токены
        """
        if self.token_storage:
            await self.token_storage.revoke_tokens_by_user(self.request.state.user.id)

        for token_type, transports in self.transports.items():
            for transport in transports:
                transport.delete_token(self.response)

    async def set_token(self, token: str, token_type: TokenType) -> None:
        for transport in self._get_transports(token_type):
            transport.set_token(self.response, token)

        if self.token_storage:
            await self.token_storage.store_token(self.token_provider.read_token(token))

    async def update_response(self, response: Response):
        """
        Добавляет обновлённый токен в response
        Нужен для middleware
        """
        if hasattr(self.request.state, "access_token"):
            access_token = self.request.state.access_token
            self.response = response

            await self.set_token(access_token, TokenType.ACCESS)

    async def refresh_access_token(self) -> None:
        """
        Обновить access токен через refresh, если тот есть
        """
        refresh_token_data = await self.read_token(TokenType.REFRESH)
        if not refresh_token_data:
            raise RefreshTokenNotValid()

        access_token = self.token_provider.create_access_token(refresh_token_data.dict())
        self.request.state.access_token = access_token
        # Так как у нас автообновление через middleware, то это лишняя работа.
        # Она полезна только при обновлении напрямую через endpoint
        if self.response:
            await self.set_token(access_token, TokenType.ACCESS)

    async def read_token(self, token_type: TokenType) -> TokenData | None:
        """Извлечь TokenData определенного типа из запроса"""
        token = self._get_access_token() if TokenType.ACCESS else self._get_refresh_token()
        token_data = self.token_provider.read_token(token)
        return await self._validate_token_or_none(token_data)

    async def _validate_token_or_none(self, token_data: TokenData) -> TokenData | None:
        """Проверка токена, в частности не отозван ли он"""
        if not token_data:
            return None

        if token_data.jti and self.token_storage:
            is_active = await self.token_storage.is_token_active(token_data.jti)
            if not is_active:
                return None

        return token_data

    def _get_access_token(self) -> str | None:
        """Получить текущий access token"""
        if hasattr(self.request.state, "access_token"):
            return self.request.state.access_token

        for transport in self._get_transports(TokenType.ACCESS):
            token = transport.get_token(self.request)
            if token is not None:
                return token

    def _get_refresh_token(self) -> str | None:
        """Получить текущий refresh token"""
        for transport in self._get_transports(TokenType.REFRESH):
            token = transport.get_token(self.request)
            if token is not None:
                return token

    def _get_transports(self, transport_type: TokenType) -> list[IAuthTransport]:
        """Получить AuthTransport по типу"""
        for token_type, transports in self.transports.items():
            if token_type == transport_type:
                return transports
        return []
