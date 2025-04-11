import pytest

from tests.users.fakes import FakeUserUnitOfWork


@pytest.fixture
def fake_user_uow():
    return FakeUserUnitOfWork()
