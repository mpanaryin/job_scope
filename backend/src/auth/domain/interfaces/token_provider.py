import abc

from src.auth.domain.entities import TokenData


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
