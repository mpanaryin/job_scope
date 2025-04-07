import os
from functools import cached_property
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    JWT_ALGORITHM: str = "ES256"
    JWT_PRIVATE_KEY_PATH: str = "./secrets/ec_private.pem"
    JWT_PUBLIC_KEY_PATH: str = "./secrets/ec_public.pem"
    # 60 seconds * 60 minutes * 24 hours * 365 day = 365 days
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 15
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 365
    SECURE_COOKIES: bool = True
    JWT_METHOD: Literal["cookies", "headers", "all"] = "all"
    JWT_ISSUER: str = "auth-service"
    JWT_HEADER_TYPE: str = "Bearer"
    JWT_ACCESS_HEADER_NAME: str = "Authorization"
    JWT_REFRESH_HEADER_NAME: str = "X-Refresh-Token"

    @cached_property
    def JWT_PRIVATE_KEY(self) -> SecretStr:
        with open(self.JWT_PRIVATE_KEY_PATH) as f:
            return SecretStr(f.read())

    @cached_property
    def JWT_PUBLIC_KEY(self) -> str:
        with open(self.JWT_PUBLIC_KEY_PATH) as f:
            return f.read()


auth_config = AuthConfig()
