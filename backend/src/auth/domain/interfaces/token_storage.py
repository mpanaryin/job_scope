import abc

from src.auth.domain.entities import TokenData


class ITokenStorage(abc.ABC):
    """
    Interface for storing and managing issued tokens.

    This abstraction allows for tracking issued tokens (e.g., storing their JTI in Redis)
    to enable advanced operations such as token revocation, validation of token activity status,
    and administrative token management.
    """

    @abc.abstractmethod
    async def store_token(self, token_data: TokenData) -> None:
        """Save token"""
        pass

    @abc.abstractmethod
    async def revoke_tokens_by_user(self, user_id: str) -> None:
        """Revoke user tokens"""
        pass

    @abc.abstractmethod
    async def is_token_active(self, jti: str) -> bool:
        """Check if the current token is active"""
        pass
