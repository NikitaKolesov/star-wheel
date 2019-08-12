from datetime import datetime, timedelta
from time import sleep

import pytest
from fastapi import HTTPException
from fastapi.security import SecurityScopes
from mimesis import Generic
from sqlalchemy.engine import Engine, create_engine
from starlette.status import HTTP_401_UNAUTHORIZED

from star_wheel.db import session_scope
from star_wheel.db.sa_models import User, Base, TelegramTimestamp
from star_wheel.schemas import UserSchema
from star_wheel.security import get_password_hash, check_telegram_login_timestamp, get_current_user, \
    create_access_token, get_current_active_user, authenticate_user

AUTH_DATE = 1565899537
fake_users_dicts = [
    {"login": "admin", "password_hash": get_password_hash("admin")},
    {"login": "user", "password_hash": get_password_hash("user")},
    {"login": "wheelov", "password_hash": get_password_hash("wheelov"), "username": "wheelov"},
]
fake_users = [User(**user_dict) for user_dict in fake_users_dicts]
ENGINE = create_engine("postgresql://postgres:qwe123QWE@localhost:5432/postgres")
DEFAULT_PASSWORD = "qwe123QWE"
generic = Generic()


@pytest.fixture(scope="session", autouse=True)
def recreate_fake_db():
    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(ENGINE)
    with session_scope() as session:
        for user in fake_users:
            user.create(session)


@pytest.fixture()
def user_in_db() -> UserSchema:
    with session_scope() as session:
        user = User(login=generic.person.username(), password_hash=get_password_hash(DEFAULT_PASSWORD)).create(
            session
        )
        return UserSchema(**user.__dict__)


@pytest.fixture()
def timestamp_in_db() -> float:
    with session_scope() as session:
        return TelegramTimestamp(timestamp=datetime.fromtimestamp(AUTH_DATE)).create(session).timestamp.timestamp()


@pytest.fixture()
def token(user_in_db):
    access_token_expires = timedelta(minutes=5)
    return create_access_token(data={"sub": user_in_db.login, "scopes": list()}, expires_delta=access_token_expires)


@pytest.fixture()
def token_expired(user_in_db):
    access_token_expires = timedelta(seconds=1)
    token = create_access_token(data={"sub": user_in_db.login, "scopes": list()}, expires_delta=access_token_expires)
    sleep(2)
    return token


@pytest.fixture()
def token_absent_user():
    access_token_expires = timedelta(minutes=5)
    return create_access_token(data={"sub": "absent_login", "scopes": list()}, expires_delta=access_token_expires)


@pytest.fixture()
def token_no_sub():
    access_token_expires = timedelta(minutes=5)
    return create_access_token(data={"scopes": list()}, expires_delta=access_token_expires)


def test_check_telegram_login_timestamp_pos(timestamp_in_db):
    assert not check_telegram_login_timestamp(timestamp_in_db)


def test_check_telegram_login_timestamp_neg():
    assert check_telegram_login_timestamp(datetime.utcnow().timestamp())


@pytest.mark.asyncio
async def test_get_current_user(token, user_in_db):
    assert await get_current_user(security_scopes=SecurityScopes(), token=token) == user_in_db


@pytest.mark.asyncio
async def test_get_current_user_expired_token(token_expired, user_in_db):
    with pytest.raises(HTTPException):
        assert await get_current_user(security_scopes=SecurityScopes(), token=token_expired) == user_in_db


@pytest.mark.asyncio
async def test_get_current_user_token_no_sub(token_no_sub):
    with pytest.raises(HTTPException):
        assert await get_current_user(security_scopes=SecurityScopes(), token=token_no_sub)


@pytest.mark.asyncio
async def test_get_current_user_absent_user(token_absent_user):
    with pytest.raises(HTTPException):
        assert await get_current_user(security_scopes=SecurityScopes(), token=token_absent_user)


@pytest.mark.asyncio
async def test_get_current_active_user_disabled(user_in_db):
    user_in_db.disabled = True
    with pytest.raises(HTTPException):
        assert await get_current_active_user(user_in_db)


@pytest.mark.asyncio
async def test_get_current_active_user_enabled(user_in_db):
    assert await get_current_active_user(user_in_db) == user_in_db


def test_authenticate_user(user_in_db):
    assert authenticate_user(user_in_db.login, DEFAULT_PASSWORD) == user_in_db


def test_authenticate_user_absent():
    assert not authenticate_user("absent_user_login", DEFAULT_PASSWORD)


def test_authenticate_user_invalid_password(user_in_db):
    assert not authenticate_user(user_in_db.login, "invalid_password")
