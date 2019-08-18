import pytest
from mimesis import Generic
from starlette.testclient import TestClient

from star_wheel import app, crud, schemas
from star_wheel.db import Base, SessionLocal, models
from tests.const import ENGINE, fake_users, DEFAULT_PASSWORD

generic = Generic()


@pytest.fixture()
def local_session():
    session = SessionLocal()
    yield session
    session.close()


# @pytest.fixture(scope="session")
@pytest.fixture(scope="session", autouse=True)
def recreate_fake_db():
    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(ENGINE)
    session = SessionLocal()
    for user in fake_users:
        crud.create_user(session, user)
    session.close()


@pytest.fixture()
def new_user() -> schemas.UserCreate:
    return schemas.UserCreate(login=generic.person.username(), password=DEFAULT_PASSWORD)


@pytest.fixture()
def user_in_db(local_session) -> models.User:
    user = schemas.UserCreate(login=generic.person.username(), password=DEFAULT_PASSWORD)
    return crud.create_user(local_session, user)


@pytest.fixture()
def authorized_client(user_in_db):
    client = TestClient(app)
    data = {"username": "user", "password": DEFAULT_PASSWORD, "grant_type": "password"}
    access_token = client.post("/token", data=data).json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client


@pytest.fixture()
def unauthorized_client(user_in_db):
    client = TestClient(app)
    return client
