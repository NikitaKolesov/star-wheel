from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from star_wheel.db import session_scope
from star_wheel.db.sa_models import User
from star_wheel.schemas import Token, TelegramUserData
from star_wheel.security import (
    get_current_active_user,
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    check_telegram_login_timestamp,
)

app = FastAPI()


@app.get("/")
async def read_items():
    return "Hello World!"


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login, "scopes": form_data.scopes}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/telegram_login", response_model=Token)
async def login_from_telegram_widget(user_data: TelegramUserData = Depends()):
    if not check_telegram_login_timestamp(user_data.auth_date):
        raise HTTPException(status_code=400, detail="Compromised authentication date")
    pass
