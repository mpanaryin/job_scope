import functools
from typing import Callable, Any

from fastapi import HTTPException
from starlette.requests import Request

from src.auth.domain.exceptions import AuthRequired
from src.auth.domain.entities import AnonymousUser
from src.core.domain.exceptions.exceptions import PermissionDenied


class access_control:  # noqa
    """
    Decorator for access control on FastAPI endpoints.

    Important: the decorated endpoint must explicitly include
    `request: Request` or `auth: TokenAuthDep` in its parameters.

    Supports checks for:
    - Superuser-only access.
    - Open access (for anonymous users).
    - Authenticated user access by default.

    Usage:
    ```
    @access_control(superuser=True)
    async def admin_view(request: Request):
        ...
    ```

    :param superuser: If True, only superusers can access the endpoint.
    :param open: If True, anonymous users are allowed. Otherwise, authentication is required.
    """

    def __init__(
        self,
        superuser: bool = False,
        open: bool = False,
    ) -> None:
        self.superuser: bool = superuser
        self.open: bool = open
        self.current_user = None
        self.request: Request | None = None
        self.headers: dict[Any, Any] | None = None
        self.auth_header: str | None = None
        self.token: str | None = None

    def __call__(self, function) -> Callable[..., Any]:
        @functools.wraps(function)
        async def decorated(*args, **kwargs):
            await self.parse_request(**kwargs)
            is_allowed = await self.verify_request(*args, **kwargs)
            if not is_allowed:
                raise HTTPException(403, "Not allowed.")
            return await function(*args, **kwargs)

        return decorated

    async def parse_request(self, **kwargs) -> None:
        """
        Extract the user from the request state and store it in `cls.current_user`.
        If no user is found, use AnonymousUser as default.
        """
        request = getattr(kwargs.get("auth"), "request", None) or kwargs.get("request")
        user = getattr(request, "state", None) and getattr(request.state, "user", None)
        self.current_user = user if user is not None else AnonymousUser()
        return None

    async def verify_request(self, *args, **kwargs) -> bool:
        """
        Perform access checks based on the parameters:
        - If `superuser=True`, ensure the current user is a superuser.
        - If `open=False`, ensure the current user is authenticated.

        :return: True if access is allowed, False or exception otherwise.
        """
        if self.superuser and not self.current_user.is_superuser:
            raise PermissionDenied()

        if isinstance(self.current_user, AnonymousUser) and not self.open:
            raise AuthRequired()

        return True
