"""SQL Alchemy models"""

import logging
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, BigInteger
from sqlalchemy.dialects.postgresql import UUID, BOOLEAN, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    uuid = Column(UUID, primary_key=True, nullable=False)
    login = Column(String, unique=True, nullable=False)
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String)
    disabled = Column(BOOLEAN, default=False)
    first_name = Column(String)
    last_name = Column(String)
    photo_url = Column(String)
    password_hash = Column(String)

    def __repr__(self):
        return f"User(login='{self.login}', username='{self.username}', telegram_id='{self.telegram_id}')"

    def create(self, session: Session) -> "User":
        """Create user in database"""
        self.uuid = str(uuid4())
        session.add(self)
        session.commit()
        log.info(f"{self} was created")
        return self

    def disable(self, session: Session) -> "User":
        self.disabled = True
        session.add(self)
        session.commit()
        log.info(f"{self} was disabled")
        return self

    @classmethod
    def from_login(cls, session: Session, login: str) -> "User":
        return session.query(cls).filter(cls.login == login).first()


class TelegramTimestamp(Base):
    __tablename__ = "timestamps"

    timestamp = Column(TIMESTAMP, primary_key=True, nullable=False)

    def create(self, session: Session):
        """Create user in database"""
        session.add(self)
        session.commit()
        log.info(f"{self} was created")
        return self

    @classmethod
    def from_db(cls, session: Session, timestamp: datetime):
        return session.query(cls).filter(cls.timestamp == timestamp).first()
