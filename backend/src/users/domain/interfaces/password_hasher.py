import abc


class IPasswordHasher(abc.ABC):

    @abc.abstractmethod
    def hash(self, password: str) -> str:
        """Generate a hash from a plain text password."""
        pass

    @abc.abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify if a plain password matches the hashed one"""
        pass
