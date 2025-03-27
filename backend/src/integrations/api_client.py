from base64 import b64encode
from enum import Enum
from typing import Literal
from urllib.parse import urljoin

import aiohttp
from aiohttp import BasicAuth, ClientResponse

from src.utils.aiohttp_client import AiohttpClient


class AuthType(Enum):
    """Тип авторизации для запросов"""
    NO = "NO"
    BASIC = "Basic"
    BEARER_TOKEN = "BearerToken"
    TOKEN_TOKEN = "TokenToken"


class TokenAuth:
    def __init__(self, token_name: str, token_value: str):
        self.token_name = token_name
        self.token_value = token_value

    def __call__(self, r):
        r.headers["Authorization"] = self.token_name + " " + self.token_value
        return r


class AuthMixin:
    """Mixin определяющий тип авторизации"""
    auth_type: AuthType
    username: str | None
    password: str | None
    token: str | None

    @property
    def auth_headers(self):
        """Создает заголовки авторизации"""
        if self.auth_type == AuthType.TOKEN_TOKEN and self.token:
            return {"Authorization": f'Token {self.token}'}
        elif self.auth_type == AuthType.BEARER_TOKEN and self.token:
            return {"Authorization": f'Bearer {self.token}'}
        elif self.auth_type == AuthType.BASIC and self.username and self.password:
            return {"Authorization": self._basic_auth_str()}
        return {}

    @staticmethod
    def _to_native_string(string, encoding="ascii"):
        """
        Данная функция принимает строковый объект, независимо от его типа, и возвращает его представление в
        родном строковом формате, выполняя кодирование и декодирование, если это необходимо.
        По умолчанию используется кодировка ASCII, если не указано иное.
        """
        if isinstance(string, str):
            out = string
        else:
            out = string.decode(encoding)
        return out

    def _basic_auth_str(self) -> str:
        """Возвращает строку Basic Auth"""
        username = self.username
        password = self.password
        if isinstance(self.username, str):
            username = self.username.encode("latin1")
        if isinstance(self.username, str):
            password = self.username.encode("latin1")
        return "Basic " + self._to_native_string(
            b64encode(b":".join((username, password))).strip()
        )


class APIClient(AuthMixin):
    """Сервис для отправки запросов"""
    def __init__(
        self,
        source_url: str,
        client: AiohttpClient = AiohttpClient,
        headers: dict | None = None,
        auth_type: AuthType = AuthType.NO,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None
    ):
        self.auth_type = auth_type
        self.username = username
        self.password = password
        self.token = token

        self.client = client
        self.source_url = source_url
        self.headers = {**(headers or {}), **self.auth_headers}

    async def request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        endpoint: str,
        json_data: dict | None = None,
        params: dict | None = None,
        headers: dict | None = None,
        **kwargs
    ) -> ClientResponse:
        headers = headers or {}
        request_params = {
            "url": urljoin(self.source_url, endpoint),
            "headers": {**self.headers, **headers},
            "json": json_data, "params": params, **kwargs
        }
        if method == "GET":
            response = await self.client.get(**request_params)
        elif method == "POST":
            response = await self.client.post(**request_params)
        elif method == "PUT":
            response = await self.client.put(**request_params)
        elif method == "DELETE":
            response = await self.client.delete(**request_params)
        elif method == "PATCH":
            response = await self.client.patch(**request_params)
        else:
            raise ValueError("Method not supported")
        response.raise_for_status()
        return response
