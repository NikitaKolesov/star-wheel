import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Union

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import SecurityScopes
from jwt import PyJWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

import star_wheel.middleware
from . import config, crud, schemas
from .db import models


def verify_password(plain_password, hashed_password):
    return config.pwd_context.verify(plain_password, hashed_password)


def create_access_token(*, data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, login: str, password: str) -> Union[models.User, bool]:
    user_in_db = crud.get_user_by_login(db, login)
    if not user_in_db:
        return False
    if not verify_password(password, user_in_db.password_hash):
        return False
    return user_in_db


async def get_current_user(
    security_scopes: SecurityScopes,
    session: Session = Depends(star_wheel.middleware.get_db),
    token: str = Depends(schemas.oauth2_scheme),
) -> models.User:
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
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = schemas.TokenData(scopes=token_scopes, login=login)
    except (PyJWTError, ValidationError):
        raise credentials_exception
    user: models.User = crud.get_user_by_username(session, login) or crud.get_user_by_login(session, login)
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


async def get_current_active_user(current_user: schemas.UserInDb = Security(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def verify_telegram_auth_data(data, bot_token):
    check_hash = data.pop("hash")
    check_list = ["{}={}".format(k, v) for k, v in data.items()]
    check_string = "\n".join(sorted(check_list))

    secret_key = hashlib.sha256(str.encode(bot_token)).digest()
    hmac_hash = hmac.new(secret_key, str.encode(check_string), hashlib.sha256).hexdigest()

    return hmac_hash == check_hash
