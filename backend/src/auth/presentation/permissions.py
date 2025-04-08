import functools
from typing import Callable, Any

from fastapi import HTTPException
from starlette.requests import Request

from src.auth.domain.exceptions import AuthRequired
from src.auth.domain.entities import AnonymousUser
from src.core.domain.exceptions import PermissionDenied


class access_control:  # noqa
    """
    Decorator for access control on FastAPI endpoints.

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
    MASTER_USER_ID = 0

    def __init__(
        self,
        # module: Optional[AppModules] = None,
        # resource: Optional[AppActions] = None,
        superuser: bool = False,
        open: bool = False,
    ) -> None:
        # cls.module = module
        # cls.resource = resource
        self.superuser: bool = superuser
        self.open: bool = open
        self.object_id: int | None = None
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
        try:
            self.current_user = kwargs['request'].state.user
        except (AttributeError, KeyError):
            self.current_user = AnonymousUser()
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
