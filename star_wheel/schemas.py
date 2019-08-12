from typing import Optional, List

from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    login: str = None
    scopes: List[str] = []


class UserSchema(BaseModel):
    login: str
    uuid: str = None
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    password_hash: Optional[str] = None
    disabled: Optional[bool] = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None


class TelegramUserData(BaseModel):
    id: int
    first_name: str
    username: str
    photo_url: str
    auth_date: float
    hash = str


SCOPES = {"me": "Read information about the current user", "root": "Root access"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", scopes=SCOPES)
