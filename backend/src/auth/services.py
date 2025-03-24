from src.auth.exceptions import InvalidCredentials
from src.auth.schemas import AuthUser
from src.auth.utils import check_password
from src.users.services import UserService


async def authenticate(credentials: AuthUser):
    """Аутентификация пользователя"""
    user = await UserService().get_by_email(credentials.email)
    if not user:
        raise InvalidCredentials()

    if not check_password(credentials.password, user.hashed_password):
        raise InvalidCredentials()
    return user
