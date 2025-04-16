import abc
from src.auth.domain.entities import TokenData, TokenType
from src.users.domain.entities import User


class ITokenProvider(abc.ABC):
    """
    Interface for working with tokens.

    This contract defines a basic set of operations for creating and reading tokens
    (e.g., access and refresh), without being tied to a specific storage or validation method.

    Main responsibilities:
    - Generate access and refresh tokens based on arbitrary data.
    - Decode and extract useful information from the token (as TokenData).

    The implementation should be stateless and synchronous,
    as all operations are performed locally (no I/O).

    Used together with ITokenAuth for full authorization support.
    """

    @abc.abstractmethod
    def create_access_token(self, data: dict) -> str:
        """Create a new access token."""
        pass

    @abc.abstractmethod
    def create_refresh_token(self, data: dict) -> str:
        """Create a new refresh token."""
        pass

    @abc.abstractmethod
    def read_token(self, token: str | None) -> TokenData | None:
        """Read a token and gets TokenData or None"""
        pass


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


class ITokenAuth(abc.ABC):
    """
    Interface for Token-based authorization mechanism.

    Acts as a bridge between the transport layer (cookies/headers...),
    the token provider, and optionally, the token storage.

    Responsibilities:
    - Manage access/refresh tokens: set, remove, refresh.
    - Read and validate tokens from the request.
    - Integrate with `ITokenProvider` (for token creation and decoding).
    - Integrate with transports (`IAuthTransport`): cookies, headers, etc.

    Intended for use in middleware, dependencies, or endpoints.

    Note: The interface is fully asynchronous, as it may interact with token storage.
    """

    def __init__(self, token_provider: ITokenProvider, token_storage: ITokenStorage | None = None):
        self.token_provider = token_provider
        self.token_storage = token_storage

    @abc.abstractmethod
    async def set_tokens(self, user: User) -> None:
        """Set new access/refresh tokens in the response."""
        pass

    @abc.abstractmethod
    async def set_token(self, token: str, token_type: TokenType) -> None:
        """Set a specific token (by type) in the response."""
        pass

    @abc.abstractmethod
    async def unset_tokens(self) -> None:
        """Remove all tokens (e.g., on logout)."""
        pass

    @abc.abstractmethod
    async def refresh_access_token(self) -> None:
        """Refresh the access token using the refresh token."""
        pass

    @abc.abstractmethod
    async def read_token(self, token_type: TokenType) -> TokenData | None:
        """Read a token from the request and return its content (TokenData) if valid."""
        pass


class IPasswordHasher(abc.ABC):
    @abc.abstractmethod
    def hash(self, password: str) -> str:
        """Generate a hash from a plain text password."""
        pass

    @abc.abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify if a plain password matches the hashed one"""
        pass
