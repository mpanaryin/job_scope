import os
from typing import Literal

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator, ValidationInfo, AnyUrl, ConfigDict
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
    ALEMBIC_DATABASE_URI: AnyUrl | None = None

    REDIS_URL: str | None = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    ELASTICSEARCH_HOSTS: str | None = os.environ.get("ELASTICSEARCH_HOSTS")

    @staticmethod
    def _build_dsn(scheme: str, values: dict) -> str:
        """Формирует DSN строку"""
        return str(
            PostgresDsn.build(
                scheme=scheme,
                username=values.get("DB_USER"),
                password=values.get("DB_PASSWORD"),
                host=values.get("DB_HOST"),
                port=int(values["DB_PORT"]) if values.get("DB_PORT") else None,
                path=values.get("DB_NAME"),
            )
        )

    @field_validator("DATABASE_URI")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if os.environ.get("ENVIRONMENT") == "testing":
            db_name = os.getenv("DB_NAME")
            db_host = os.getenv("DB_HOST")
            if "test" not in db_name and "test" not in db_host:
                raise RuntimeError("Testing mode enabled, but DB_NAME and DB_HOST does not look like test database.")

        if isinstance(v, str):
            return v
        db_type = info.data.get("DB_TYPE")
        if db_type == "SQLITE":
            return f"sqlite:///{info.data.get('DB_NAME')}.db"
        elif db_type == "ASYNC_SQLITE":
            return f"sqlite+aiosqlite:///{info.data.get('DB_NAME')}.db"
        elif db_type == "POSTGRESQL":
            return cls._build_dsn("postgresql+psycopg", info.data)
        elif db_type == "ASYNC_POSTGRESQL":
            return cls._build_dsn("postgresql+asyncpg", info.data)
        raise ValueError("Unsupported database type")

    @field_validator("ALEMBIC_DATABASE_URI", mode="before")
    def assemble_alembic_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        db_type = info.data.get("DB_TYPE")
        if db_type in ["SQLITE", "POSTGRESQL"]:
            return info.data.get("DATABASE_URI")  # sync
        elif db_type == "ASYNC_SQLITE":
            return f"sqlite:///{info.data.get('DB_NAME')}.db"
        elif db_type == "ASYNC_POSTGRESQL":
            return cls._build_dsn("postgresql+psycopg", info.data)
        raise ValueError("Unsupported DB_TYPE for alembic")

    SMTP_TLS: bool = True
    SMTP_PORT: int | None = None
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAIL_FROM: EmailStr | None = None

    model_config = ConfigDict()


settings = Settings()
