import abc
from src.auth.domain.entities import TokenData, TokenType
from src.users.domain.entities import User


class ITokenProvider(abc.ABC):

    @abc.abstractmethod
    def create_access_token(self, data: dict) -> str:
        pass

    @abc.abstractmethod
    def create_refresh_token(self, data: dict) -> str:
        pass

    @abc.abstractmethod
    def read_token(self, token: str | None) -> TokenData | None:
        pass


class ITokenStorageService(abc.ABC):

    @abc.abstractmethod
    async def store_token(self, token_data: TokenData) -> None:
        """Сохранить токен"""
        ...

    @abc.abstractmethod
    async def revoke_tokens_by_user(self, user_id: str) -> None:
        """Отозвать токены пользователя"""
        ...

    @abc.abstractmethod
    async def is_token_active(self, jti: str) -> bool:
        """Проверить активен ли текущей токен"""
        ...


class ITokenAuth(abc.ABC):
    def __init__(self, token_provider: ITokenProvider):
        self.token_provider = token_provider

    @abc.abstractmethod
    async def set_tokens(self, user: User) -> None:
        ...

    @abc.abstractmethod
    async def set_token(self, token: str, token_type: TokenType) -> None:
        ...

    @abc.abstractmethod
    async def unset_tokens(self) -> None:
        ...

    @abc.abstractmethod
    async def refresh_access_token(self) -> None:
        ...

    @abc.abstractmethod
    async def read_token(self, token_type: TokenType) -> TokenData | None:
        ...

