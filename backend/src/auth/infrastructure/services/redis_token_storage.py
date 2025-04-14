from src.auth.domain.entities import TokenData
from src.auth.domain.interfaces import ITokenStorage
from src.utils.datetimes import get_timezone_now
from src.core.infrastructure.clients.redis import get_redis_client


class RedisTokenStorage(ITokenStorage):
    """
    Redis-based implementation of ITokenStorage.

    Stores JWT token metadata for validation and revocation.
    Each token is stored by its JTI and associated with a user for mass revocation.
    """

    def __init__(self):
        self.redis = get_redis_client()

    async def store_token(self, token_data: TokenData) -> None:
        """
        Store the token metadata in Redis.

        :param token_data: The decoded token data including expiration and JTI.
        """
        key = f"tokens:{token_data.jti}"
        ttl = int((token_data.exp - get_timezone_now()).total_seconds())

        # Store the token with TTL
        await self.redis.setex(key, ttl, token_data.user_id)

        # Add token JTI to the user's token set
        await self.redis.sadd(f"user_tokens:{token_data.user_id}", token_data.jti)

    async def revoke_tokens_by_user(self, user_id: str) -> None:
        """
        Revoke all tokens associated with a specific user.

        :param user_id: The ID of the user whose tokens should be revoked.
        """
        token_keys = await self.redis.smembers(f"user_tokens:{user_id}")
        for jti in token_keys:
            await self.redis.delete(f"tokens:{jti}")
        await self.redis.delete(f"user_tokens:{user_id}")

    async def is_token_active(self, jti: str) -> bool:
        """
        Check if a token with the given JTI is still active (not revoked or expired).

        :param jti: JWT ID of the token.
        :return: True if the token is active, False otherwise.
        """
        return await self.redis.exists(f"tokens:{jti}") == 1
