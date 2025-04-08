import redis.asyncio as redis
from functools import lru_cache

from src.core.config import settings


@lru_cache
def get_redis_client() -> redis.Redis:
    """
    Create and cache a Redis client instance.

    This function initializes a singleton Redis connection using the provided REDIS_URL
    from settings. The use of `lru_cache` ensures that only one Redis connection
    is created and reused throughout the application lifetime.

    :return: A cached Redis client instance.
    """
    return redis.from_url(
        url=settings.REDIS_URL,
        decode_responses=True,
        encoding="utf-8"
    )
