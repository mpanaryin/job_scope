from fastapi import status
from src.core.exc import NotFound, AlreadyExists


class UserAlreadyExists(AlreadyExists):
    status_code = status.HTTP_409_CONFLICT
    detail = "User with this data already exists"


class UserNotFound(NotFound):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User with this data not found"
