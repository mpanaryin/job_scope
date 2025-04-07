from fastapi import APIRouter

from src.crud.router import CRUDRouter
from src.users.application.use_cases.user_delete import delete_user
from src.users.application.use_cases.user_profile import get_user_profile
from src.users.application.use_cases.user_registration import register_user
from src.users.application.use_cases.user_update import update_user
from src.users.domain.dtos import UserCreateDTO, UserUpdateDTO, UserReadDTO
from src.users.infrastructure.db.crud import UserService
from src.users.infrastructure.db.unit_of_work import PGUserUnitOfWork


user_api_router = APIRouter()


@user_api_router.post("", response_model=UserReadDTO)
async def register(user_data: UserCreateDTO):
    return await register_user(user_data, uow=PGUserUnitOfWork())


@user_api_router.get("/{user_id}", response_model=UserReadDTO)
async def get_profile(user_id: int):
    return await get_user_profile(user_id, uow=PGUserUnitOfWork())


@user_api_router.patch("/{user_id}", response_model=UserReadDTO)
async def update(user_id: int, user_data: UserUpdateDTO):
    return await update_user(user_id, user_data, uow=PGUserUnitOfWork())


@user_api_router.delete("/{user_id}")
async def delete(user_id: int):
    return await delete_user(user_id, uow=PGUserUnitOfWork())


class UserCRUDRouter(CRUDRouter):
    crud = UserService()
    create_schema = UserCreateDTO
    update_schema = UserUpdateDTO
    read_schema = UserReadDTO
    router = APIRouter()
