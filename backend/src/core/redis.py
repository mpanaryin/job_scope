import redis.asyncio as redis
from functools import lru_cache

from src.core.config import settings


@lru_cache
def get_redis():
    return redis.from_url(
        url=settings.REDIS_URL,
        decode_responses=True,
        encoding="utf-8"
    )
