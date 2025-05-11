import abc
from typing import TypeVar

from src.auth.domain.entities import TokenType, TokenData
from src.auth.domain.interfaces.token_provider import ITokenProvider
from src.auth.domain.interfaces.token_storage import ITokenStorage
from src.users.domain.entities import User

TResponse = TypeVar("TResponse")


class ITokenAuth(abc.ABC):
    """
    Interface for Token-based authorization mechanism.

    Acts as a bridge between the transports layer (cookies/headers...),
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

    @abc.abstractmethod
    async def inject_access_token_from_request(self, response: TResponse) -> None:
        """
        Middleware-specific method.

        If a refreshed access token was stored during request processing,
        inject it into the outgoing response.

        This is intended for use within middleware only.
        """
        pass
