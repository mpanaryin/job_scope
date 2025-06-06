from typing import Annotated

from fastapi import APIRouter, Body

from src.auth.application.use_cases.authentication import authenticate
from src.auth.presentation.dependencies import TokenAuthDep, PasswordHasherDep
from src.auth.presentation.permissions import access_control
from src.auth.presentation.dtos import AuthUserDTO
from src.users.domain.dtos import UserReadDTO
from src.users.presentation.dependencies import UserUoWDep

auth_api_router = APIRouter()


@auth_api_router.post("/login")
async def login(
    credentials: AuthUserDTO,
    pwd_hasher: PasswordHasherDep,
    uow: UserUoWDep,
    auth: TokenAuthDep
):
    """
    Authenticate user and issue JWT tokens.
    """
    await authenticate(credentials.email, credentials.password, pwd_hasher, uow, auth)
    return {"detail": "Tokens set"}


@auth_api_router.post("/logout")
async def logout(auth: TokenAuthDep):
    """
    Log out the current user and revoke all active tokens.
    """
    await auth.unset_tokens()
    return {"detail": "Tokens deleted"}


@auth_api_router.post("/refresh")
async def refresh(auth: TokenAuthDep):
    """
    Refresh the access token using a valid refresh token.
    """
    await auth.refresh_access_token()
    return {"detail": "The token has been refresh"}


@auth_api_router.post("/revoke")
@access_control(superuser=True)
async def revoke_tokens(user_id: Annotated[int, Body(embed=True)], auth: TokenAuthDep):
    """
    Revoke all tokens for a specific user by ID (admin action).
    """
    await auth.token_storage.revoke_tokens_by_user(user_id)
    return {"detail": f"Tokens revoked for user {user_id}"}


@auth_api_router.get("/me")
@access_control(open=True)
async def get_me(auth: TokenAuthDep) -> UserReadDTO:
    """
    Retrieve the profile of the currently authenticated user.
    """
    return auth.request.state.user
