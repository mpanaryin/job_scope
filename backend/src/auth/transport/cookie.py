from typing import Literal

from fastapi import Response, status
from fastapi.security import APIKeyCookie

from src.auth.transport.base import Transport


class CookieTransport(Transport):
    scheme: APIKeyCookie

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
        self.cookie_name = cookie_name
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite
        self.scheme = APIKeyCookie(name=self.cookie_name, auto_error=False)

    def set_login_cookie(self, response: Response, token: str):
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

    def delete_cookie(self, response: Response):
        response.delete_cookie(
            key=self.cookie_name,
            path=self.cookie_path,
            domain=self.cookie_domain,
        )
