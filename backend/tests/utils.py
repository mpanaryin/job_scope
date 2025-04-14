from contextlib import asynccontextmanager

from src.main import app


@asynccontextmanager
async def override_dependencies(overrides: dict):
    app.dependency_overrides.update(overrides)
    try:
        yield
    finally:
        app.dependency_overrides = {}
