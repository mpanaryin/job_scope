from typing import Annotated

from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response

from src.auth.jwt import JWTAuth


async def get_jwt_auth(request: Request, response: Response) -> JWTAuth:
    return JWTAuth(request, response)

JWTAuthDep = Annotated[JWTAuth, Depends(get_jwt_auth)]
