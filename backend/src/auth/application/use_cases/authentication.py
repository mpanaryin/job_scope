from src.auth.domain.exceptions import InvalidCredentials
from src.auth.domain.interfaces.token_auth import ITokenAuth
from src.users.domain.entities import User
from src.users.domain.interfaces.password_hasher import IPasswordHasher
from src.users.domain.interfaces.user_uow import IUserUnitOfWork


async def authenticate(
    email: str,
    password: str,
    pwd_hasher: IPasswordHasher,
    uow: IUserUnitOfWork,
    auth: ITokenAuth
) -> User:
    """
    Authenticate a user using the provided credentials.

    Verifies the user's email and password combination,
    and if valid, sets access and refresh tokens.

    :param email: User email.
    :param password: User password.
    :param pwd_hasher: Password hasher
    :param uow: Unit of work to access user repository.
    :param auth: JWT authentication service for setting tokens.
    :raises InvalidCredentials: If the password is incorrect.
    :return: User instance.
    """
    async with uow:
        user = await uow.users.get_by_email(email)

        if not pwd_hasher.verify(password, user.hashed_password):
            raise InvalidCredentials()

        await auth.set_tokens(user)
        return user
