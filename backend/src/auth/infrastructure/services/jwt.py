import uuid6
from datetime import timedelta
from typing import Any
from jose import jwt, JWTError
from pydantic import SecretStr
from starlette.requests import Request
from starlette.responses import Response

from src.auth.domain.entities import TokenData, TokenType
from src.auth.config import auth_config
from src.auth.domain.exceptions import RefreshTokenNotValid
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.auth.domain.interfaces.token_provider import ITokenProvider
from src.auth.domain.interfaces.token_storage import ITokenStorage
from src.auth.infrastructure.transports.base import IAuthTransport
from src.users.domain.entities import User
from src.utils.datetimes import get_timezone_now

SecretType = str | SecretStr


class JWTProvider(ITokenProvider):
    """
    Service for encoding and decoding JWT tokens.
    """

    def create_access_token(self, data: dict) -> str:
        """
        Create an access token with configured expiration.

        :param data: Payload to include in the token.
        :return: Encoded JWT access token as a string.
        """
        return self._encode_jwt(
            data=data,
            secret=auth_config.JWT_PRIVATE_KEY,
            lifetime_seconds=auth_config.ACCESS_TOKEN_EXPIRE_SECONDS,
        )

    def create_refresh_token(self, data: dict) -> str:
        """
        Create a refresh token with configured expiration.

        :param data: Payload to include in the token.
        :return: Encoded JWT refresh token as a string.
        """
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
        """
        Encode payload into a JWT.

        :param data: Payload to encode.
        :param secret: Secret or private key for signing.
        :param lifetime_seconds: Optional token expiration duration in seconds.
        :param algorithm: JWT signing algorithm.
        :return: Encoded JWT token string.
        """
        payload = data.copy()
        if lifetime_seconds:
            expire = get_timezone_now() + timedelta(seconds=lifetime_seconds)
            payload["exp"] = expire
        payload["jti"] = str(uuid6.uuid6())  # JWT ID
        payload["iss"] = auth_config.JWT_ISSUER
        return jwt.encode(payload, self._get_secret_value(secret), algorithm=algorithm)

    def read_token(self, token: str | None) -> TokenData | None:
        """
        Decode and validate a JWT token.

        :param token: Encoded JWT token string.
        :return: TokenData if valid and contains user_id, else None.
        """
        if token is None:
            return None

        try:
            data = self._decode_jwt(token, auth_config.JWT_PUBLIC_KEY, algorithms=[auth_config.JWT_ALGORITHM])
            user_id = data.get("user_id")
            if user_id is None:
                return None
            return TokenData(**data)
        except JWTError:
            return None

    def _decode_jwt(
        self,
        encoded_jwt: str,
        secret: SecretType,
        algorithms: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Decode a JWT and verify its signature and claims.

        :param encoded_jwt: Encoded JWT string.
        :param secret: Secret or public key for verification.
        :param algorithms: List of accepted algorithms.
        :return: Decoded JWT payload as a dictionary.
        """
        if algorithms is None:
            algorithms = [auth_config.JWT_ALGORITHM]
        return jwt.decode(
            token=encoded_jwt,
            key=self._get_secret_value(secret),
            algorithms=algorithms,
            issuer=auth_config.JWT_ISSUER
        )

    def _get_secret_value(self, secret: SecretType) -> str:
        """
        Extract string value from a SecretStr or return plain string.

        :param secret: Secret value (either plain string or SecretStr).
        :return: String representation of the secret.
        """
        if isinstance(secret, SecretStr):
            return secret.get_secret_value()
        return secret


class JWTAuth(ITokenAuth):
    """
    Implementation of ITokenAuth for handling JWT-based authentication.

    Provides methods to issue, revoke, refresh, and retrieve access/refresh tokens
    from the request/response cycle.
    Integrates with a token storage backend for additional validation like token revocation.
    """

    def __init__(
        self,
        token_provider: ITokenProvider,
        transports: dict[TokenType, list[IAuthTransport]],
        token_storage: ITokenStorage | None = None,
        request: Request | None = None,
        response: Response | None = None
    ):
        """
        :param token_provider: JWT token provider instance.
        :param transports: Dictionary of token transports for each token type.
        :param token_storage: Optional token storage for revocation and validation.
        :param request: Current HTTP request (can be None in some contexts).
        :param response: Current HTTP response for setting tokens (can be None in some contexts).
        """
        super().__init__(token_provider, token_storage)
        self.transports = transports
        self.request = request
        self.response = response

    async def set_tokens(self, user: User) -> None:
        """
        Generate and store access and refresh tokens for a given user.
        Sets them in the HTTP response.

        :param user: Authenticated user entity.
        """
        data = {
            "user_id": str(user.id),
            "is_superuser": user.is_superuser,
        }
        access_token = self.token_provider.create_access_token(data)
        refresh_token = self.token_provider.create_refresh_token(data)
        await self.set_token(access_token, TokenType.ACCESS)
        await self.set_token(refresh_token, TokenType.REFRESH)

    async def set_token(self, token: str, token_type: TokenType) -> None:
        """
        Set a single token (access or refresh) in the response and persist it if required.

        :param token: JWT token string.
        :param token_type: Type of token (access or refresh).
        """
        for transport in self._get_transports(token_type):
            transport.set_token(self.response, token)

        if self.token_storage:
            await self.token_storage.store_token(self.token_provider.read_token(token))

    async def unset_tokens(self) -> None:
        """
        Revoke all tokens of the current user and remove them from the response.
        """
        if self.token_storage:
            await self.token_storage.revoke_tokens_by_user(self.request.state.user.id)

        for token_type, transports in self.transports.items():
            for transport in transports:
                transport.delete_token(self.response)

    async def inject_access_token_from_request(self, response: Response):
        """
        Inject the updated access token into the response.

        Useful in middleware when token is refreshed automatically.

        :param response: Outgoing HTTP response to update.
        """
        if hasattr(self.request.state, "access_token"):
            access_token = self.request.state.access_token
            self.response = response

            await self.set_token(access_token, TokenType.ACCESS)

    async def refresh_access_token(self) -> None:
        """
        Refresh the access token using a valid refresh token.
        Sets the new access token in the request and optionally in the response.

        :raises RefreshTokenNotValid: If refresh token is missing or invalid.
        """
        refresh_token_data = await self.read_token(TokenType.REFRESH)
        if not refresh_token_data:
            raise RefreshTokenNotValid()

        access_token = self.token_provider.create_access_token(
            refresh_token_data.model_dump(include={"user_id", "is_superuser"})
        )

        # Optimized self.set_token functionality for use via API/middleware
        self.request.state.access_token = access_token

        if self.token_storage:
            await self.token_storage.store_token(self.token_provider.read_token(access_token))

        # Since we have auto-update via middleware, this is extra work.
        # It is only useful when updating directly via the endpoint
        if self.response:
            for transport in self._get_transports(TokenType.ACCESS):
                transport.set_token(self.response, access_token)

    async def read_token(self, token_type: TokenType) -> TokenData | None:
        """
        Retrieve and validate token data for a given token type.

        :param token_type: Type of token (access or refresh).
        :return: TokenData if valid and active, else None.
        """
        token = self._get_access_token() if token_type == TokenType.ACCESS else self._get_refresh_token()
        token_data = self.token_provider.read_token(token)
        return await self._validate_token_or_none(token_data)

    async def _validate_token_or_none(self, token_data: TokenData) -> TokenData | None:
        """
        Validate a token using the storage backend.

        :param token_data: Decoded token data.
        :return: TokenData if valid, else None.
        """
        if not token_data:
            return None

        if token_data.jti and self.token_storage:
            is_active = await self.token_storage.is_token_active(token_data.jti)
            if not is_active:
                return None
        return token_data

    def _get_access_token(self) -> str | None:
        """
        Retrieve access token from the request.

        :return: Access token string or None.
        """
        if hasattr(self.request.state, "access_token"):
            return self.request.state.access_token

        for transport in self._get_transports(TokenType.ACCESS):
            token = transport.get_token(self.request)
            if token is not None:
                return token

    def _get_refresh_token(self) -> str | None:
        """
        Retrieve refresh token from the request.

        :return: Refresh token string or None.
        """
        for transport in self._get_transports(TokenType.REFRESH):
            token = transport.get_token(self.request)
            if token is not None:
                return token

    def _get_transports(self, transport_type: TokenType) -> list[IAuthTransport]:
        """
        Get all transports configured for the given token type.

        :param transport_type: Token type (access or refresh).
        :return: List of configured IAuthTransport instances.
        """
        for token_type, transports in self.transports.items():
            if token_type == transport_type:
                return transports
        return []
