import pytest

from tests.fakes.users import FakeUserUnitOfWork


@pytest.fixture
def fake_user_uow():
    return FakeUserUnitOfWork()
