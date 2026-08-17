"""
Tests for the User Management CRUD module.

Runs against an in-memory SQLite database, so no PostgreSQL connection
is needed to execute these tests.

Run with:
    pytest tests/test_users.py -v
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
import app.models  # noqa: F401
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import DuplicateUserError, UserService


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    yield session
    session.close()


@pytest.fixture
def service(db_session):
    return UserService(db_session)


def make_user(service, n):
    return service.create_user(
        UserCreate(
            username=f"user{n}",
            email=f"user{n}@test.com",
            full_name=f"User {n}",
            password="password123",
        )
    )


def test_create_five_users(service):
    users = [make_user(service, i) for i in range(1, 6)]
    assert len(users) == 5
    assert all(u.id is not None for u in users)


def test_retrieve_users(service):
    for i in range(1, 6):
        make_user(service, i)
    all_users = service.list_users()
    assert len(all_users) == 5


def test_update_two_users(service):
    for i in range(1, 6):
        make_user(service, i)

    updated_1 = service.update_user(1, UserUpdate(full_name="Updated One"))
    updated_2 = service.update_user(2, UserUpdate(is_active=False))

    assert updated_1.full_name == "Updated One"
    assert updated_2.is_active is False


def test_delete_user(service):
    for i in range(1, 6):
        make_user(service, i)

    result = service.delete_user(5)
    assert result is True


def test_retrieve_deleted_user_returns_none(service):
    for i in range(1, 6):
        make_user(service, i)

    service.delete_user(5)
    assert service.get_user(5) is None


def test_create_user_with_existing_username_raises(service):
    make_user(service, 1)

    with pytest.raises(DuplicateUserError):
        service.create_user(
            UserCreate(
                username="user1",
                email="different@test.com",
                password="password123",
            )
        )
