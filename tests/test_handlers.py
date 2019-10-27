from uuid import UUID, uuid4

from star_wheel import schemas
from star_wheel.db import models
from tests import const


def test_read_users_me(authorized_user, user_in_db: models.User):
    response = authorized_user.get("/users/me")
    assert response.json()["login"] == "user"
    assert UUID(response.json()["id"])


def test_create_user(authorized_user, new_user: schemas.UserCreate):
    response = authorized_user.post("/users", json=new_user.dict())
    assert response.json()["login"] == new_user.login
    assert response.status_code == 201


def test_login_from_telegram_widget(unauthorized_user):
    response = unauthorized_user.post("/telegram_login", json=const.TELEGRAM_AUTH_DATA)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_from_telegram_widget_consequent(unauthorized_user):
    response = unauthorized_user.post("/telegram_login", json=const.TELEGRAM_AUTH_DATA)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_from_telegram_widget_invalid(unauthorized_user):
    const.TELEGRAM_AUTH_DATA["first_name"] = "NotNikita"
    response = unauthorized_user.post("/telegram_login", json=const.TELEGRAM_AUTH_DATA)
    assert response.status_code == 400
    assert response.json() == {"detail": "Compromised telegram user data"}


def test_get_user(authorized_user, user_in_db: models.User):
    response = authorized_user.get(f"/users/{user_in_db.id}")
    assert response.status_code == 200
    assert response.json()["login"] == user_in_db.login


def test_get_absent_user(authorized_user):
    response = authorized_user.get(f"/users/{uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_delete_user(authorized_user, user_in_db: models.User):
    response = authorized_user.delete(f"/users/{user_in_db.id}")
    assert response.status_code == 200
    response = authorized_user.get(f"/users/{user_in_db.id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_question(authorized_user):
    response = authorized_user.post("/questions", json=const.question_create_dict)
    assert response.status_code == 200


def test_get_user_questions(authorized_user, user_in_db):
    response = authorized_user.get(f"/users/{user_in_db.id}/questions")
    assert response.status_code == 200
