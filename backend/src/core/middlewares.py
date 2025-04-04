from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.auth.exceptions import RefreshTokenNotValid
from src.auth.jwt import JWTAuth
from src.auth.schemas import AnonymousUser
from src.users.services import UserService


class JWTRefreshMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        pre_auth = JWTAuth(request=request)
        access_data = pre_auth.read_access_token()
        if access_data is None:
            try:
                pre_auth.refresh_access_token()
            except RefreshTokenNotValid:
                # Не смогли обновить токен, продолжаем обычный запрос
                ...
        response = await call_next(request)
        # Нужно проверить, остался ли refresh токен,
        # иначе будет баг с продлением access
        post_auth = JWTAuth(request=request, response=response)
        if post_auth.read_refresh_token():
            pre_auth.update_response(response)
        # Токен валидный, продолжаем
        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Добавление пользователя в запрос
        jwt_auth = JWTAuth(request=request)
        token_data = jwt_auth.read_access_token()
        if not token_data:
            request.state.user = AnonymousUser()
        else:
            user = await UserService().get_by_pk(token_data.user_id)
            request.state.user = user or AnonymousUser()
        # Продолжение обработки запроса
        response = await call_next(request)
        return response


class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secure_paths: list | None = None, allowed_paths: list | None = None):
        super().__init__(app)
        self.secure_paths = secure_paths
        # Доступные ссылки
        self.allowed_paths = allowed_paths

    async def dispatch(self, request: Request, call_next):
        # Закрытые ссылки
        if self.secure_paths is None:
            self.secure_paths = ["/api", "/admin", "/docs", "/redoc"]
        # Доступные ссылки
        if self.allowed_paths is None:
            self.allowed_paths = ["/api/users/login", "/api/users/logout", "/api/users/refresh",]
        if not request.state.user.is_superuser and any(
            [True if secure_path in str(request.url) else False for secure_path in self.secure_paths]
        ) and not any([True if allowed_path in str(request.url) else False for allowed_path in self.allowed_paths]):
            return JSONResponse(
                status_code=403,
                content={"message": "Permission Denied"}
            )
        # Продолжение обработки запроса
        response = await call_next(request)
        return response
