from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.auth.domain.entities import AnonymousUser, TokenType
from src.auth.domain.exceptions import RefreshTokenNotValid
from src.auth.presentation.dependencies import get_jwt_auth
from src.users.infrastructure.db.unit_of_work import PGUserUnitOfWork


class JWTRefreshMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically refresh an access token using a valid refresh token.

    If an access token is missing or invalid, it attempts to refresh it.
    The refreshed access token is set in the response if a valid refresh token exists.
    """

    async def dispatch(self, request: Request, call_next):
        pre_auth = await get_jwt_auth(request=request)
        access_data = await pre_auth.read_token(TokenType.ACCESS)
        if access_data is None:
            try:
                await pre_auth.refresh_access_token()
            except RefreshTokenNotValid:
                # Token couldn't be refreshed – fallback to anonymous request
                ...
        response = await call_next(request)
        # Ensure refresh token is still valid before updating response with new access
        post_auth = await get_jwt_auth(request=request, response=response)
        refresh_data = await post_auth.read_token(TokenType.REFRESH)

        if refresh_data:
            await pre_auth.update_response(response)

        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that injects the authenticated user into `request.state.user`.

    If no valid access token is found, the user is treated as anonymous.
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        jwt_auth = await get_jwt_auth(request=request)
        token_data = await jwt_auth.read_token(TokenType.ACCESS)
        if not token_data:
            request.state.user = AnonymousUser()
        else:
            async with PGUserUnitOfWork() as uow:
                user = await uow.users.get_by_pk(token_data.user_id)
                request.state.user = user or AnonymousUser()

        response = await call_next(request)
        return response


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to restrict access to secure paths.

    If the current user is not a superuser and tries to access a protected path
    that is not explicitly allowed, a 403 response is returned.
    """

    def __init__(self, app, secure_paths: list | None = None, allowed_paths: list | None = None):
        """
        :param app: FastAPI application
        :param secure_paths: List of base paths considered protected.
        :param allowed_paths: List of paths that are publicly accessible even within protected zones.
        """
        super().__init__(app)
        self.secure_paths = secure_paths or ["/api", "/admin", "/docs", "/redoc"]
        self.allowed_paths = allowed_paths or [
            "/api/users/login", "/api/users/logout", "/api/users/refresh", "/api/users/me"
        ]

    async def dispatch(self, request: Request, call_next):
        request_path = str(request.url)

        is_protected_path = any(path in request_path for path in self.secure_paths)
        is_allowed_path = any(path in request_path for path in self.allowed_paths)

        if is_protected_path and not is_allowed_path and not request.state.user.is_superuser:
            return JSONResponse(
                status_code=403,
                content={"message": "Permission Denied"}
            )

        response = await call_next(request)
        return response
