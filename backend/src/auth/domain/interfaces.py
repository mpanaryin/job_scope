import abc
from typing import Literal
from src.auth.domain.entities import TokenData
from src.users.domain.entities import User


class ITokenProvider(abc.ABC):

    @abc.abstractmethod
    def create_access_token(self, data: dict) -> str:
        pass

    @abc.abstractmethod
    def create_refresh_token(self, data: dict) -> str:
        pass

    @abc.abstractmethod
    def read_token(self, token: str | None, token_type: Literal['access', 'refresh']) -> TokenData | None:
        pass


class ITokenAuth(abc.ABC):
    def __init__(self, token_provider: ITokenProvider):
        self.token_provider = token_provider

    @abc.abstractmethod
    def set_tokens(self, user: User) -> None:
        ...

    @abc.abstractmethod
    def unset_tokens(self) -> None:
        ...

    @abc.abstractmethod
    def set_access_token(self, access_token: str) -> None:
        ...

    @abc.abstractmethod
    def set_refresh_token(self, refresh_token: str) -> None:
        ...

    @abc.abstractmethod
    def refresh_access_token(self) -> None:
        ...

    @abc.abstractmethod
    def read_access_token(self) -> TokenData | None:
        ...

    @abc.abstractmethod
    def read_refresh_token(self) -> TokenData | None:
        ...
