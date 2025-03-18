import functools
import time
from typing import Callable, Any

from fastapi import HTTPException
from starlette.requests import Request

from src.auth.exceptions import AuthRequired
from src.auth.schemas import AnonymousUser
from src.core.exceptions import PermissionDenied


class access_control:  # pylint: disable=invalid-name
    MASTER_USER_ID = 0

    def __init__(
        cls,
        # module: Optional[AppModules] = None,
        # resource: Optional[AppActions] = None,
        superuser: bool = False,
        open: bool = False,
    ) -> None:
        # cls.module = module
        # cls.resource = resource
        cls.superuser: bool = superuser
        cls.open: bool = open
        cls.object_id: int | None = None
        cls.current_user = None
        cls.request: Request | None = None
        cls.headers: dict[Any, Any] | None = None
        cls.auth_header: str | None = None
        cls.token: str | None = None

    def __call__(cls, function) -> Callable[..., Any]:
        @functools.wraps(function)
        async def decorated(*args, **kwargs):
            t0 = time.time()
            await cls.parse_request(**kwargs)
            is_allowed = await cls.verify_request(*args, **kwargs)
            if not is_allowed:
                raise HTTPException(403, "Not allowed.")
            return await function(*args, **kwargs)

        return decorated

    async def parse_request(cls, **kwargs) -> None:
        """Получаем пользователя из запроса"""
        try:
            cls.current_user = kwargs['request'].state.user
        except (AttributeError, KeyError):
            cls.current_user = AnonymousUser()
        return None

    async def verify_request(cls, *args, **kwargs) -> bool:
        """Проверяем доступы, описываем условия доступа"""
        if cls.superuser and not cls.current_user.is_superuser:
            raise PermissionDenied()
        if isinstance(cls.current_user, AnonymousUser) and not cls.open:
            raise AuthRequired()

        return True
