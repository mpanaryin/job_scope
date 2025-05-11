from src.core.domain.exceptions.exceptions import AlreadyExists, NotFound


class UserAlreadyExists(AlreadyExists):
    detail = "User with this data already exists"


class UserNotFound(NotFound):
    detail = "User with this data not found"
