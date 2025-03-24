import os
import secrets
from typing import Any, Literal

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator, ValidationInfo, AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = os.environ.get("PROJECT_NAME", "UNNAMED PROJECT")
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.environ.get("SECRET_KEY")  # secrets.token_urlsafe(32)
    DOMAIN: str = os.environ.get("DOMAIN")
    SSL_ENABLED: bool = os.environ.get("SSL_ENABLED")
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: str | list[str]) -> str | list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    DB_TYPE: Literal['POSTGRESQL', 'ASYNC_POSTGRESQL', 'SQLITE', 'ASYNC_SQLITE'] = os.environ.get("DB_TYPE")
    DB_NAME: str = os.environ.get("DB_NAME")
    DB_USER: str | None = os.environ.get("DB_USER")
    DB_PASSWORD: str | None = os.environ.get("DB_PASSWORD")
    DB_HOST: str | None = os.environ.get("DB_HOST")
    DB_PORT: str | None = os.environ.get("DB_PORT")
    DATABASE_URI: AnyUrl | None = None

    ELASTICSEARCH_URL: str = os.environ.get("ELASTICSEARCH_URL")

    @field_validator("DATABASE_URI")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        """Собираем соединение к БД"""
        if isinstance(v, str):
            return v
        db_type = info.data.get("DB_TYPE")
        if db_type == "SQLITE":
            return f"sqlite:///{info.data.get('DB_NAME')}.db"
        elif db_type == "ASYNC_SQLITE":
            return f"sqlite+aiosqlite:///{info.data.get('DB_NAME')}.db"
        elif db_type == "POSTGRESQL":
            scheme = "postgresql+psycopg"
        elif db_type == "ASYNC_POSTGRESQL":
            scheme = "postgresql+asyncpg"
        else:
            raise ValueError("Unsupported database type")
        return PostgresDsn.build(
            scheme=scheme,
            username=info.data.get("DB_USER"),
            password=info.data.get("DB_PASSWORD"),
            host=info.data.get("DB_HOST"),
            port=int(info.data.get("DB_PORT")) if info.data.get("DB_PORT") else None,
        )

    SMTP_TLS: bool = True
    SMTP_PORT: int | None = None
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    @field_validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: str | None, info: ValidationInfo) -> str:
        if not v:
            return info.data["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/src/src/email-templates/build"
    EMAILS_ENABLED: bool = False

    @field_validator("EMAILS_ENABLED")
    def get_emails_enabled(cls, v: bool, info: ValidationInfo) -> bool:
        return bool(
            info.data.get("SMTP_HOST")
            and info.data.get("SMTP_PORT")
            and info.data.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "mytest@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    class Config:
        case_sensitive = True


settings = Settings()
