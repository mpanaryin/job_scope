import bcrypt

from src.auth.domain.interfaces import IPasswordHasher


class BcryptPasswordHasher(IPasswordHasher):

    def hash(self, password: str) -> str:
        """
        Generate a bcrypt hash from a plain text password.

        :param password: Plain text password.
        :return: Hashed password as a UTF-8 encoded string.
        """
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode("utf-8")

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify if a plain password matches the hashed one.

        :param plain_password: Plain text password to check.
        :param hashed_password: Hashed password stored in the database.
        :return: True if the password matches, False otherwise.
        """
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
