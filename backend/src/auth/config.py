import os
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_SECRET: SecretStr = SecretStr(os.environ.get("JWT_ACCESS_SECRET"))
    JWT_REFRESH_SECRET: SecretStr = SecretStr(os.environ.get("JWT_REFRESH_SECRET"))
    # 60 seconds * 60 minutes * 24 hours * 365 day = 365 days
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 15
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 365
    SECURE_COOKIES: bool = True
    JWT_METHOD: Literal["cookies", "headers", "both"] = "both"
    JWT_HEADER_TYPE: str = "Bearer"
    JWT_ACCESS_HEADER_NAME: str = "Authorization"
    JWT_REFRESH_HEADER_NAME: str = "X-Refresh-Token"


auth_config = AuthConfig()
