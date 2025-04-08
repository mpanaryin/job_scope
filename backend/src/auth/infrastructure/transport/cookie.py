from typing import Literal

from starlette.requests import Request
from starlette.responses import Response

from src.auth.infrastructure.transport.base import IAuthTransport


class CookieTransport(IAuthTransport):
    """
    Transport strategy using cookies to manage tokens in HTTP requests and responses.
    """

    def __init__(
        self,
        cookie_name: str,
        cookie_max_age: int | None = None,
        cookie_path: str = "/",
        cookie_domain: str | None = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: Literal["lax", "strict", "none"] = "lax",
    ):
        """
        Initialize cookie transport.

        :param cookie_name: Name of the cookie to store the token.
        :param cookie_max_age: Cookie expiration time in seconds.
        :param cookie_path: Path for which the cookie is valid.
        :param cookie_domain: Domain for which the cookie is valid.
        :param cookie_secure: Whether to use the Secure flag.
        :param cookie_httponly: Whether to use the HttpOnly flag.
        :param cookie_samesite: SameSite policy for the cookie.
        """
        self.cookie_name = cookie_name
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite

    def set_token(self, response: Response, token: str) -> None:
        """
        Set the token in a cookie within the HTTP response.

        :param response: The outgoing HTTP response.
        :param token: The token to be set.
        """
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            max_age=self.cookie_max_age,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )

    def delete_token(self, response: Response) -> None:
        """
        Delete the token cookie from the HTTP response.

        :param response: The outgoing HTTP response.
        """
        response.delete_cookie(
            key=self.cookie_name,
            path=self.cookie_path,
            domain=self.cookie_domain,
        )

    def get_token(self, request: Request) -> str | None:
        """
        Retrieve the token from the incoming request's cookies.

        :param request: The incoming HTTP request.
        :return: Token string or None.
        """
        return request.cookies.get(self.cookie_name, None)
