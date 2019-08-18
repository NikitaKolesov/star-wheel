from random import choice

from star_wheel.crud import *
from tests.const import fake_users


def test_get_user_by_login(local_session):
    user: schemas.UserCreate = choice(fake_users)
    assert get_user_by_login(local_session, user.login).login == user.login
