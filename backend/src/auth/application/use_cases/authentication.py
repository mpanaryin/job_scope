from src.auth.domain.dtos import AuthUserDTO
from src.auth.domain.exceptions import InvalidCredentials
from src.auth.domain.interfaces import ITokenAuth, IPasswordHasher
from src.users.domain.entities import User
from src.users.domain.interfaces import IUserUnitOfWork


async def authenticate(
    credentials: AuthUserDTO,
    pwd_hasher: IPasswordHasher,
    uow: IUserUnitOfWork,
    auth: ITokenAuth
) -> User:
    """
    Authenticates a user based on provided credentials.

    Verifies the user's email and password combination, and if valid, sets access and refresh tokens.

    :param credentials: User credentials (email and password).
    :param pwd_hasher: Password hasher
    :param uow: Unit of work to access user repository.
    :param auth: JWT authentication service for setting tokens.
    :raises InvalidCredentials: If the password is incorrect.
    :return: User instance.
    """
    async with uow:
        user = await uow.users.get_by_email(credentials.email)

        if not pwd_hasher.verify(credentials.password, user.hashed_password):
            raise InvalidCredentials()

        await auth.set_tokens(user)
        return user
