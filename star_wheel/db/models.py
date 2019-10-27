"""SQL Alchemy models"""

import logging
from typing import MutableMapping, Any
from uuid import uuid4

from sqlalchemy import BigInteger, Column, String
from sqlalchemy.dialects.postgresql import BOOLEAN, TIMESTAMP, UUID

from star_wheel.db import Base

log = logging.getLogger(__name__)


def str_uuid():
    return str(uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, nullable=False, default=str_uuid)
    login = Column(String, unique=True)
    telegram_id = Column(BigInteger, unique=True)
    disabled = Column(BOOLEAN, default=False)
    first_name = Column(String)
    last_name = Column(String)
    photo_url = Column(String)
    password_hash = Column(String)

    def __repr__(self) -> str:
        return f"User(login='{self.login}', telegram_id='{self.telegram_id}')"

    def dict(self) -> MutableMapping[str, Any]:
        return self.__dict__


class TelegramTimestamp(Base):
    __tablename__ = "timestamps"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP, nullable=False)
    telegram_id = Column(BigInteger, nullable=False)
