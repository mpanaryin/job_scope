from base64 import b64encode
from enum import Enum
from typing import Literal
from urllib.parse import urljoin

from src.integrations.domain.interfaces import IAsyncHttpClient


class AuthType(Enum):
    """
    Type of authorization used in HTTP requests.
    """
    NO = "NO"
    BASIC = "Basic"
    BEARER_TOKEN = "BearerToken"
    TOKEN_TOKEN = "TokenToken"


class AuthMixin:
    """
    Mixin that provides authorization headers for HTTP requests.

    Supports multiple authorization schemes, such as Bearer, Token, and Basic.
    """
    auth_type: AuthType
    username: str | None
    password: str | None
    token: str | None

    @property
    def auth_headers(self):
        """
        Generate the appropriate authorization headers based on the configured auth type.

        :return: A dictionary with the "Authorization" header if applicable, otherwise empty.
        """
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
        Convert a byte or string object into a native string.

        :param string: String or bytes to convert.
        :param encoding: Encoding used to decode bytes (default is "ascii").
        :return: A native Python string.
        """
        if isinstance(string, str):
            out = string
        else:
            out = string.decode(encoding)
        return out

    def _basic_auth_str(self) -> str:
        """
        Generate the Basic authorization header value.

        :return: A string like "Basic dXNlcjpwYXNz".
        """
        username = self.username
        password = self.password
        if isinstance(self.username, str):
            username = self.username.encode("latin1")
        if isinstance(self.password, str):
            password = self.password.encode("latin1")
        return "Basic " + self._to_native_string(
            b64encode(b":".join((username, password))).strip()
        )


class APIClientService(AuthMixin):
    """
    Generic HTTP client service with built-in authentication support.

    This service is designed to abstract the logic of sending HTTP requests to external APIs.
    It supports various authentication types (e.g., Bearer, Basic)
    and uses an injected asynchronous HTTP client that conforms to the IAsyncHttpClient interface.

    Args:
        source_url: Base URL of the external API.
        client: Asynchronous HTTP client implementation (e.g., AiohttpClient).
        headers: Optional additional headers to include in every request.
        auth_type: Authorization type (NO, BASIC, BEARER_TOKEN, TOKEN_TOKEN).
        username: Username for basic authentication.
        password: Password for basic authentication.
        token: Access token (for Bearer or Token schemes).

    Methods:
        request(...): Send an HTTP request using the configured method and parameters.
    """
    def __init__(
        self,
        source_url: str,
        client: IAsyncHttpClient,
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
    ):
        """
        Execute an HTTP request using the configured method and parameters.

        :param method: HTTP method to use (GET, POST, PUT, DELETE, PATCH).
        :param endpoint: Relative path to the resource on the external API.
        :param json_data: Optional JSON body.
        :param params: Optional query parameters.
        :param headers: Optional additional headers.
        :param kwargs: Extra keyword arguments passed to the HTTP client.
        :return: HTTP response from the external service.
        :raises ValueError: If the provided method is unsupported.
        """
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
