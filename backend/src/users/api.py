from fastapi import APIRouter

from src.crud.router import CRUDRouter
from src.users import schemas
from src.users.services import UserService


class UserCRUDRouter(CRUDRouter):
    crud = UserService()
    create_schema = schemas.UserCreate
    update_schema = schemas.UserUpdate
    read_schema = schemas.User
    router = APIRouter()
