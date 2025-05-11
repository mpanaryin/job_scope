from functools import cached_property
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    """
    Configuration for JWT-based authentication.

    This class manages all JWT-related settings, including algorithm,
    token expiration, key paths, and token transports settings.

    Attributes:
        JWT_ALGORITHM: Algorithm used for signing tokens (e.g., ES256).
        JWT_PRIVATE_KEY_PATH: Path to the private key PEM file.
        JWT_PUBLIC_KEY_PATH: Path to the public key PEM file.
        ACCESS_TOKEN_EXPIRE_SECONDS: Lifetime of access tokens in seconds.
        REFRESH_TOKEN_EXPIRE_SECONDS: Lifetime of refresh tokens in seconds.
        SECURE_COOKIES: Whether to use `Secure` flag for cookies.
        JWT_METHOD: Where to read/write JWT tokens (cookies, headers, or both).
        JWT_ISSUER: Issuer claim (`iss`) to embed in JWT.
        JWT_HEADER_TYPE: Prefix in the Authorization header (e.g., "Bearer").
        JWT_ACCESS_HEADER_NAME: Header name for access token.
        JWT_REFRESH_HEADER_NAME: Header name for refresh token.
    """
    JWT_ALGORITHM: str = "ES256"
    JWT_PRIVATE_KEY_PATH: str = "./secrets/ec_private.pem"
    JWT_PUBLIC_KEY_PATH: str = "./secrets/ec_public.pem"
    # 60 seconds * 60 minutes * 24 hours * 30 day = 30 days
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 15
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 30
    SECURE_COOKIES: bool = True
    JWT_METHOD: Literal["cookies", "headers", "all"] = "all"
    JWT_ISSUER: str = "auth-service"
    JWT_HEADER_TYPE: str = "Bearer"
    JWT_ACCESS_HEADER_NAME: str = "Authorization"
    JWT_REFRESH_HEADER_NAME: str = "X-Refresh-Token"

    @cached_property
    def JWT_PRIVATE_KEY(self) -> SecretStr:
        """
        Lazily loads and returns the private key used for signing JWT tokens.

        :return: The contents of the PEM-formatted private key as a `SecretStr`.
        """
        with open(self.JWT_PRIVATE_KEY_PATH) as f:
            return SecretStr(f.read())

    @cached_property
    def JWT_PUBLIC_KEY(self) -> SecretStr:
        """
        Lazily loads and returns the public key used for verifying JWT tokens.

        :return: The contents of the PEM-formatted public key as a `SecretStr`.
        """
        with open(self.JWT_PUBLIC_KEY_PATH) as f:
            return SecretStr(f.read())


auth_config = AuthConfig()
