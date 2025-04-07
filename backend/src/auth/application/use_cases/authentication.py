from src.auth.domain.entities import AuthUser
from src.auth.domain.exceptions import InvalidCredentials
from src.auth.domain.interfaces import ITokenAuth
from src.auth.infrastructure.services.password import check_password
from src.users.domain.interfaces import IUserUnitOfWork


async def authenticate(credentials: AuthUser, uow: IUserUnitOfWork, auth: ITokenAuth):
    """Аутентификация пользователя"""
    async with uow:
        user = await uow.users.get_by_email(credentials.email)

        if not check_password(credentials.password, user.hashed_password):
            raise InvalidCredentials()

        await auth.set_tokens(user)
        return user
