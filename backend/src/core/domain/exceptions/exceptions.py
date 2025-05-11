from src.core.domain.exceptions import statuses


class AppException(Exception):
    """
    Base application exception.

    This class is used as the foundation for all custom exceptions in the app.
    It includes HTTP status code, a human-readable message, and optional context.

    Attributes:
        status_code (int): HTTP status code associated with the exception.
        detail (str): A human-readable message describing the error.
        extra (dict | None): Additional context or metadata to include in the response.

    Note:
        HTTP status codes are used intentionally even at the domain/application level
        because they are widely familiar, easy to interpret, and cover most common cases.
        If a mismatch between internal status and external requirements occurs,
        it can easily be resolved with a mapper at the infrastructure or presentation level.

        Defining a separate internal status system would introduce unnecessary complexity
        for developers accustomed to web applications, so HTTP codes are a pragmatic choice.
    """
    status_code = statuses.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Server error"
    extra: dict | None = None

    def __init__(
        self,
        status_code: int | None = None,
        detail: str | None = None,
        **kwargs
    ) -> None:
        self.status_code = self.status_code if not status_code else status_code
        self.detail = self.detail if not detail else detail
        self.extra = self.extra if not kwargs else kwargs
        super().__init__(self.detail)


class PermissionDenied(AppException):
    status_code = statuses.HTTP_403_FORBIDDEN
    detail = "Permission denied"


class NotFound(AppException):
    status_code = statuses.HTTP_404_NOT_FOUND
    detail = "Not found"


class AlreadyExists(AppException):
    status_code = statuses.HTTP_409_CONFLICT
    detail = "Already exists"


class BadRequest(AppException):
    status_code = statuses.HTTP_400_BAD_REQUEST
    detail = "Bad Request"


class NotAuthenticated(AppException):
    status_code = statuses.HTTP_401_UNAUTHORIZED
    detail = "User not authenticated"
