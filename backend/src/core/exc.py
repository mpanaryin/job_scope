from fastapi import status


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Server error"
    kwargs: dict | None = None

    def __init__(
        self,
        status_code: int | None = None,
        detail: str | None = None,
        **kwargs
    ) -> None:
        self.status_code = self.status_code if not status_code else status_code
        self.detail = self.detail if not detail else detail
        self.kwargs = self.kwargs if not kwargs else kwargs
        super().__init__(self.detail)


class PermissionDenied(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Permission denied"


class NotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Not found"


class AlreadyExists(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Already exists"


class BadRequest(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad Request"


class NotAuthenticated(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "User not authenticated"

    def __init__(self) -> None:
        super().__init__(headers={"WWW-Authenticate": "Bearer"})
