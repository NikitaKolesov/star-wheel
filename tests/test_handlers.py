from uuid import UUID, uuid4

from starlette.testclient import TestClient

from star_wheel import schemas
from star_wheel.db import models
from tests.const import TELEGRAM_AUTH_DATA


def test_read_users_me(authorized_client: TestClient, user_in_db: models.User):
    response = authorized_client.get("/users/me")
    assert response.json()["login"] == "user"
    assert UUID(response.json()["id"])


def test_create_user(authorized_client: TestClient, new_user: schemas.UserCreate):
    response = authorized_client.post("/users", json=new_user.dict())
    assert response.json()["login"] == new_user.login
    assert response.status_code == 201


def test_login_from_telegram_widget(unauthorized_client: TestClient):
    response = unauthorized_client.post("/telegram_login", json=TELEGRAM_AUTH_DATA)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_from_telegram_widget_consequent(unauthorized_client: TestClient):
    response = unauthorized_client.post("/telegram_login", json=TELEGRAM_AUTH_DATA)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_from_telegram_widget_invalid(unauthorized_client: TestClient):
    TELEGRAM_AUTH_DATA["first_name"] = "NotNikita"
    response = unauthorized_client.post("/telegram_login", json=TELEGRAM_AUTH_DATA)
    assert response.status_code == 400
    assert response.json() == {"detail": "Compromised telegram user data"}


def test_get_user(authorized_client: TestClient, user_in_db: models.User):
    response = authorized_client.get(f"/users/{user_in_db.id}")
    assert response.status_code == 200
    assert response.json()["login"] == user_in_db.login


def test_get_absent_user(authorized_client: TestClient):
    response = authorized_client.get(f"/users/{uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_delete_user(authorized_client: TestClient, user_in_db: models.User):
    response = authorized_client.delete(f"/users/{user_in_db.id}")
    assert response.status_code == 200
    response = authorized_client.get(f"/users/{user_in_db.id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
