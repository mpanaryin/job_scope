from src.auth.domain.entities import TokenData
from src.auth.domain.interfaces import ITokenStorageService
from src.utils.datetimes import get_timezone_now
from src.core.redis import get_redis


class RedisTokenStorageService(ITokenStorageService):
    def __init__(self):
        self.redis = get_redis()

    async def store_token(self, token_data: TokenData) -> None:
        """Сохранить токен в Redis"""
        # Сохраняем токен
        key = f"tokens:{token_data.jti}"
        ttl = int((token_data.exp - get_timezone_now()).total_seconds())
        await self.redis.setex(key, ttl, token_data.user_id)
        # Привязываем токен к пользователю, добавляя его во множество
        await self.redis.sadd(f"user_tokens:{token_data.user_id}", token_data.jti)
        await self.redis.expire(f"user_tokens:{token_data.user_id}", ttl)

    async def revoke_tokens_by_user(self, user_id: str) -> None:
        """Удаляем токены пользователя"""
        token_keys = await self.redis.smembers(f"user_tokens:{user_id}")
        for jti in token_keys:
            await self.redis.delete(f"tokens:{jti}")
        await self.redis.delete(f"user_tokens:{user_id}")

    async def is_token_active(self, jti: str) -> bool:
        """Быстрый поиск токена"""
        return await self.redis.exists(f"tokens:{jti}") == 1
