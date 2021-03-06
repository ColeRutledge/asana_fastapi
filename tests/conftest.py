from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.auth.auth_utils import get_current_user
from app.config import get_settings, Settings
from app.db import get_db
from app.main import create_application
from app.models import Base, User
from migrations.seed import seed_db


SQLALCHEMY_TEST_DATABASE_URL = 'sqlite:///app_test.db'
# SQLALCHEMY_TEST_DATABASE_URL = 'sqlite://'
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={'check_same_thread': False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_test_settings():
    return Settings(db_url=SQLALCHEMY_TEST_DATABASE_URL)


def override_get_current_user():
    return User(
        id=1,
        first_name='Test',
        last_name='User',
        email='test@user.com',
        team_id=1,
        hashed_password='password')


def override_get_db():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope='module')
def test_app():
    app = create_application()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = override_test_settings
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine, checkfirst=True)
    yield from override_get_db()
    Base.metadata.drop_all(bind=engine)

    # Base.metadata.create_all(bind=engine, checkfirst=True)
    # db_session = Session(autocommit=False, autoflush=False, bind=engine)
    # yield db_session
    # db_session.close()
    # Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db_seeded(test_db: Session):
    seed_db(test_db)
    yield test_db
