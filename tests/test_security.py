from datetime import datetime, timedelta
from time import sleep

import pytest
from fastapi import HTTPException
from fastapi.security import SecurityScopes

from star_wheel.db import models, session_scope
from star_wheel import schemas, security
from tests.const import AUTH_DATE, DEFAULT_PASSWORD, generic


@pytest.fixture()
def user_in_db() -> schemas.UserInDb:
    with session_scope() as session:
        user = models.User(
            login=generic.person.username(), password_hash=security.get_password_hash(DEFAULT_PASSWORD)
        ).create(session)
        return schemas.UserInDb(**user.__dict__)


@pytest.fixture()
def timestamp_in_db() -> float:
    with session_scope() as session:
        return (
            models.TelegramTimestamp(timestamp=datetime.fromtimestamp(AUTH_DATE)).create(session).timestamp.timestamp()
        )


@pytest.fixture()
def token(user_in_db):
    access_token_expires = timedelta(minutes=5)
    return security.create_access_token(
        data={"sub": user_in_db.login, "scopes": list()}, expires_delta=access_token_expires
    )


@pytest.fixture()
def token_with_scope(user_in_db):
    access_token_expires = timedelta(minutes=5)
    return security.create_access_token(
        data={"sub": user_in_db.login, "scopes": ["custom_scope"]}, expires_delta=access_token_expires
    )


@pytest.fixture()
def token_expired(user_in_db):
    access_token_expires = timedelta(seconds=1)
    token = security.create_access_token(
        data={"sub": user_in_db.login, "scopes": list()}, expires_delta=access_token_expires
    )
    sleep(2)
    return token


@pytest.fixture()
def token_absent_user():
    access_token_expires = timedelta(minutes=5)
    return security.create_access_token(
        data={"sub": "absent_login", "scopes": list()}, expires_delta=access_token_expires
    )


@pytest.fixture()
def token_no_sub():
    access_token_expires = timedelta(minutes=5)
    return security.create_access_token(data={"scopes": list()}, expires_delta=access_token_expires)


def test_check_telegram_login_timestamp_pos(timestamp_in_db):
    assert not security.validate_telegram_login_timestamp(timestamp_in_db)


def test_check_telegram_login_timestamp_neg():
    assert security.validate_telegram_login_timestamp(datetime.utcnow().timestamp())


@pytest.mark.asyncio
async def test_get_current_user(token, user_in_db):
    assert await security.get_current_user(security_scopes=SecurityScopes(), token=token) == user_in_db


@pytest.mark.asyncio
async def test_get_current_user_with_custom_scope(token_with_scope, user_in_db):
    assert (
        await security.get_current_user(security_scopes=SecurityScopes(["custom_scope"]), token=token_with_scope)
        == user_in_db
    )


@pytest.mark.asyncio
async def test_get_current_user_with_wrong_scope(token_with_scope, user_in_db):
    with pytest.raises(HTTPException):
        assert await security.get_current_user(
            security_scopes=SecurityScopes(["invalid_scope"]), token=token_with_scope
        )


@pytest.mark.asyncio
async def test_get_current_user_expired_token(token_expired, user_in_db):
    with pytest.raises(HTTPException):
        assert await security.get_current_user(security_scopes=SecurityScopes(), token=token_expired) == user_in_db


@pytest.mark.asyncio
async def test_get_current_user_token_no_sub(token_no_sub):
    with pytest.raises(HTTPException):
        assert await security.get_current_user(security_scopes=SecurityScopes(), token=token_no_sub)


@pytest.mark.asyncio
async def test_get_current_user_absent_user(token_absent_user):
    with pytest.raises(HTTPException):
        assert await security.get_current_user(security_scopes=SecurityScopes(), token=token_absent_user)


@pytest.mark.asyncio
async def test_get_current_active_user_disabled(user_in_db):
    user_in_db.disabled = True
    with pytest.raises(HTTPException):
        assert await security.get_current_active_user(user_in_db)


@pytest.mark.asyncio
async def test_get_current_active_user_enabled(user_in_db):
    assert await security.get_current_active_user(user_in_db) == user_in_db


def test_authenticate_user(user_in_db):
    assert security.authenticate_user(user_in_db.login, DEFAULT_PASSWORD) == user_in_db


def test_authenticate_user_absent():
    assert not security.authenticate_user("absent_user_login", DEFAULT_PASSWORD)


def test_authenticate_user_invalid_password(user_in_db):
    assert not security.authenticate_user(user_in_db.login, "invalid_password")
