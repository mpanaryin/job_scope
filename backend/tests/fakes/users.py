from src.users.domain.entities import UserCreate, User, UserUpdate
from src.users.domain.exceptions import UserNotFound
from src.users.domain.interfaces.user_repo import IUserRepository
from src.users.domain.interfaces.user_uow import IUserUnitOfWork


class FakeUserRepository(IUserRepository):
    def __init__(self):
        self._users = []
        self._last_user_id = 0

    async def add(self, user: UserCreate) -> User:
        user = User(id=self._get_new_user_id(), **user.model_dump())
        self._users.append(user)
        return user

    async def get_by_pk(self, pk: int) -> User:
        for user in self._users:
            if user.id == pk:
                return user

        raise UserNotFound(detail=f"User with id {pk} not found")

    async def get_by_email(self, email: str) -> User:
        for user in self._users:
            if user.email == email:
                return user

        raise UserNotFound(detail=f"User with email {email} not found")

    async def update(self, user_data: UserUpdate) -> User:
        user = await self.get_by_pk(user_data.id)

        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        return user

    async def delete(self, pk: int) -> None:
        user = await self.get_by_pk(pk)
        self._users.remove(user)

    def _get_new_user_id(self) -> int:
        self._last_user_id += 1
        return self._last_user_id


class FakeUserUnitOfWork(IUserUnitOfWork):
    users: IUserRepository

    def __init__(self):
        self.users = FakeUserRepository()
        self.committed = False

    async def _commit(self):
        self.committed = True

    async def rollback(self):
        pass
