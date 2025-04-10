from fastapi import APIRouter
from starlette.requests import Request

from src.auth.application.use_cases.authentication import authenticate
from src.auth.presentation.dependencies import JWTAuthDep, TokenStorageDep
from src.auth.presentation.permissions import access_control
from src.auth.domain.dtos import AuthUserDTO
from src.users.domain.dtos import UserReadDTO
from src.users.presentation.dependencies import UserUoWDep

auth_api_router = APIRouter()


@auth_api_router.post("/login")
async def login(credentials: AuthUserDTO, auth: JWTAuthDep, uow: UserUoWDep):
    """
    Authenticate user and issue JWT tokens.
    """
    await authenticate(credentials, uow, auth)
    return {"msg": "Tokens set"}


@auth_api_router.post("/logout")
async def logout(auth: JWTAuthDep):
    """
    Log out the current user and revoke all active tokens.
    """
    await auth.unset_tokens()
    return {"msg": "Tokens deleted"}


@auth_api_router.post("/refresh")
async def refresh(auth: JWTAuthDep):
    """
    Refresh the access token using a valid refresh token.
    """
    await auth.refresh_access_token()
    return {"msg": "The token has been refresh"}


@auth_api_router.post("/users/{user_id}/tokens/revoke")
async def revoke_tokens(user_id: str, token_storage: TokenStorageDep):
    """
    Revoke all tokens for a specific user by ID (admin action).
    """
    await token_storage.revoke_tokens_by_user(user_id)
    return {"msg": f"Tokens revoked for user {user_id}"}


@auth_api_router.get("/me")
@access_control(open=True)
async def get_my_account(request: Request) -> UserReadDTO:
    """
    Retrieve the profile of the currently authenticated user.
    """
    return request.state.user
