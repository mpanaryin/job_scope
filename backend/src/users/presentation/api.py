from fastapi import APIRouter

from src.auth.presentation.dependencies import PWDHasherDep
from src.crud.router import CRUDRouter
from src.users.application.use_cases.user_delete import delete_user
from src.users.application.use_cases.user_profile import get_user_profile
from src.users.application.use_cases.user_registration import register_user
from src.users.application.use_cases.user_update import update_user
from src.users.domain.dtos import UserCreateDTO, UserUpdateDTO, UserReadDTO
from src.users.infrastructure.db.crud import UserService
from src.users.presentation.dependencies import UserUoWDep

user_api_router = APIRouter()


@user_api_router.post("", response_model=UserReadDTO)
async def register(user_data: UserCreateDTO, pwd_hasher: PWDHasherDep, uow: UserUoWDep):
    """
    Register a new user.
    """
    return await register_user(user_data, pwd_hasher=pwd_hasher, uow=uow)


@user_api_router.get("/{user_id}", response_model=UserReadDTO)
async def get_profile(user_id: int, uow: UserUoWDep):
    """
    Get user profile by ID.
    """
    return await get_user_profile(user_id, uow=uow)


@user_api_router.patch("/{user_id}", response_model=UserReadDTO)
async def update(user_id: int, user_data: UserUpdateDTO, uow: UserUoWDep):
    """
    Update user data.
    """
    return await update_user(user_id, user_data, uow=uow)


@user_api_router.delete("/{user_id}")
async def delete(user_id: int, uow: UserUoWDep):
    """
    Delete user by ID.
    """
    return await delete_user(user_id, uow=uow)


class UserCRUDRouter(CRUDRouter):
    """
    CRUD router configuration for the user entity.

    Attributes:
        crud: User service implementing CRUDBase.
        create_schema: Schema for user creation.
        update_schema: Schema for user update.
        read_schema: Schema for reading user data.
        router: FastAPI router instance.
    """
    crud = UserService()
    create_schema = UserCreateDTO
    update_schema = UserUpdateDTO
    read_schema = UserReadDTO
    router = APIRouter()
