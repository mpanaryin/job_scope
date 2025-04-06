import abc

from starlette.requests import Request
from starlette.responses import Response


class IAuthTransport(abc.ABC):
    @abc.abstractmethod
    def set_token(self, response: Response, token: str) -> None:
        """Добавить токен в ответ"""
        ...

    @abc.abstractmethod
    def delete_token(self, response: Response) -> None:
        """Удалить токен из ответа"""
        ...

    @abc.abstractmethod
    def get_token(self, request: Request) -> str | None:
        """Получить токен"""
        ...
