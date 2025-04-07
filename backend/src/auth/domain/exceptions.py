from src.core.exc import BadRequest, NotAuthenticated


class ErrorCode:
    AUTHENTICATION_REQUIRED = "Authentication required."
    AUTHORIZATION_FAILED = "Authorization failed. User has no access."
    INVALID_TOKEN = "Invalid token."
    INVALID_CREDENTIALS = "Invalid credentials."
    EMAIL_TAKEN = "Email is already taken."
    REFRESH_TOKEN_NOT_VALID = "Refresh token is not valid."
    REFRESH_TOKEN_REQUIRED = "Refresh token is required either in the body or cookie."


class AuthRequired(NotAuthenticated):
    detail = ErrorCode.AUTHENTICATION_REQUIRED


class AuthorizationFailed(NotAuthenticated):
    detail = ErrorCode.AUTHORIZATION_FAILED


class InvalidToken(NotAuthenticated):
    detail = ErrorCode.INVALID_TOKEN


class InvalidCredentials(NotAuthenticated):
    detail = ErrorCode.INVALID_CREDENTIALS


class EmailTaken(BadRequest):
    detail = ErrorCode.EMAIL_TAKEN


class RefreshTokenRequired(BadRequest):
    detail = ErrorCode.REFRESH_TOKEN_REQUIRED


class RefreshTokenNotValid(NotAuthenticated):
    detail = ErrorCode.REFRESH_TOKEN_NOT_VALID
