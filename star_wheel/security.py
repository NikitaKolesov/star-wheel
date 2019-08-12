from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import SecurityScopes
from jwt import PyJWTError
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

from star_wheel.db import session_scope
from star_wheel.db.sa_models import User, TelegramTimestamp
from star_wheel.schemas import oauth2_scheme, TokenData, UserSchema

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(*, data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(login: str, password: str):
    with session_scope() as session:
        user: User = User.from_login(session, login=login)
        if not user:
            return False
        if not verify_password(password, user.password_hash):
            return False
        return UserSchema(**user.__dict__)


def get_user(session: Session, login: str) -> UserSchema:
    user: User = User.from_login(session, login=login)
    if user:
        return UserSchema(**user.__dict__)


async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)) -> UserSchema:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, login=login)
    except (PyJWTError, ValidationError):
        raise credentials_exception
    with session_scope() as session:
        user: UserSchema = get_user(session, login)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(current_user: UserSchema = Security(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def check_telegram_login_timestamp(timestamp: float) -> bool:
    with session_scope() as session:
        if TelegramTimestamp.from_db(session, datetime.fromtimestamp(timestamp)):
            return False
    return True
