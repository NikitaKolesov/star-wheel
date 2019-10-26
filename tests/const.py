from mimesis import Generic
from sqlalchemy import create_engine

from star_wheel import schemas

AUTH_DATA = {
    "id": 224282757,
    "first_name": "Nikita",
    "username": "wheelov",
    "photo_url": "https://t.me/i/userpic/320/u3QkAFzZQqugQszk0OwYvvSsBrOw923GjCM1LiU-VSc.jpg",
    "auth_date": 1565899537,
    "hash": "3ee3d6b0617dad1b0d42a38126af399e679b8656e2872087e56c83d36c0b45a9",
}
AUTH_DATA_K = {
    "id": 269813866,
    "first_name": "Екатерина",
    "last_name": "К",
    "username": "wheelov",
    "photo_url": "https://t.me/i/userpic/320/y4wgSrKaPPKAeSAHOX_R7aNQDbZ8xCnVawLGPA5eI_c.jpg",
    "auth_date": 1571776362,
    "hash": "88ad3d4bb55de1202360e9354e63165bd09063decdbee85a565861d8981efb0e",
}
DEFAULT_PASSWORD = "qwe123QWE"
fake_users_dicts = [
    {"login": "admin", "password": DEFAULT_PASSWORD},
    {"login": "user", "password": DEFAULT_PASSWORD},
    {"login": "wheelov", "password": DEFAULT_PASSWORD},
]
fake_users = [schemas.UserCreate(**user_dict) for user_dict in fake_users_dicts]
ENGINE = create_engine("postgresql://postgres:qwe123QWE@localhost:5432/postgres")
