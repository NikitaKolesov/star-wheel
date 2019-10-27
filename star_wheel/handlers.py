from datetime import timedelta
from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.params import Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import app, crud, config, middleware, schemas, security
from .db import models


@app.get("/")
async def read_items():
    return "Hello World!"


@app.get("/users/me")
async def read_users_me(current_user: models.User = Depends(security.get_current_active_user)):
    return current_user


@app.get("/users/{user_id}")
async def read_users_me(user_id: UUID, current_user: models.User = Depends(security.get_current_active_user)):
    user = crud.get_user(Session.object_session(current_user), user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/users/{user_id}")
async def delete_user(user_id: UUID, current_user: models.User = Depends(security.get_current_active_user)):
    crud.delete_user(Session.object_session(current_user), user_id)


@app.get("/users")
async def get_all_users(
    skip: int = 0, limit: int = 100, current_user: models.User = Depends(security.get_current_active_user)
):
    return crud.get_users(Session.object_session(current_user), skip, limit)


@app.post("/users", response_model=schemas.UserInDb, status_code=201)
async def create_user(
    new_user: schemas.UserCreate, current_user: models.User = Depends(security.get_current_active_user)
):
    created_user: models.User = crud.create_user(Session.object_session(current_user), new_user)
    return created_user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(middleware.get_db)
):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.login, "scopes": form_data.scopes}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/telegram_login", response_model=schemas.Token)
async def login_from_telegram_widget(auth_data: schemas.TelegramUserData, db: Session = Depends(middleware.get_db)):
    """Custom docstring for telegram login"""
    if not security.verify_telegram_auth_data(auth_data.dict(), config.BOT_TOKEN):
        raise HTTPException(status_code=400, detail="Compromised telegram user data")
    user_in_db = crud.get_user_by_login(db, auth_data.username)
    if not user_in_db:
        user_in_db = crud.create_user_from_telegram_auth_data(db, auth_data)
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user_in_db.login, "scopes": schemas.Scopes.USER.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/{user_id}/questions")
async def get_user_questions(
    skip: int = 0, limit: int = 100, current_user: models.User = Depends(security.get_current_active_user)
):
    return crud.get_user_questions(
        db=Session.object_session(current_user), user_id=current_user.id, limit=limit, skip=skip
    )


@app.get("/questions", response_model=List[schemas.QuestionInDb])
async def get_questions(
    skip: int = 0, limit: int = 100, current_user: models.User = Depends(security.get_current_active_user)
):
    # TODO add user protection
    return crud.get_questions(db=Session.object_session(current_user), limit=limit, skip=skip)


@app.get("/questions/{question_id}", response_model=schemas.QuestionInDb)
async def get_question(
    question_id: UUID = Path(..., title="The ID of the question to get"),
    current_user: models.User = Depends(security.get_current_active_user),
):
    # TODO add user protection
    return crud.get_question(db=Session.object_session(current_user), question_id=question_id)


@app.post("/questions", response_model=schemas.QuestionInDb)
async def create_question(
    question: schemas.Question, current_user: models.User = Depends(security.get_current_active_user)
):
    return crud.create_question(db=Session.object_session(current_user), question=question, user_id=current_user.id)
