from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from . import config, schemas
from .db import models


# User
def get_password_hash(password):
    return config.pwd_context.hash(password)


def get_user(db: Session, user_id: UUID) -> models.User:
    return db.query(models.User).filter(models.User.id == str(user_id)).first()


def get_user_by_login(db: Session, login: str) -> models.User:
    return db.query(models.User).filter(models.User.login == login).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(login=user.login, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user_from_telegram_auth_data(db: Session, auth_data: schemas.TelegramUserData) -> models.User:
    db_user = models.User(
        telegram_id=auth_data.id,
        login=auth_data.username,
        first_name=auth_data.first_name,
        photo_url=auth_data.photo_url,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: UUID):
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()


# TelegramTimestamp
def get_telegram_timestamp(db: Session, timestamp: float):
    return (
        db.query(models.TelegramTimestamp)
        .filter(models.TelegramTimestamp.timestamp == datetime.fromtimestamp(timestamp))
        .first()
    )


def delete_telegram_timestamp(db: Session, timestamp: float):
    timestamp_db = get_telegram_timestamp(db, timestamp)
    db.delete(timestamp_db)
