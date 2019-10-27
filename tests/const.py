from mimesis import Generic
from sqlalchemy import create_engine

from star_wheel import schemas

generic = Generic()

TELEGRAM_AUTH_DATA = {
    "id": 224282757,
    "first_name": "Nikita",
    "username": "wheelov",
    "photo_url": "https://t.me/i/userpic/320/u3QkAFzZQqugQszk0OwYvvSsBrOw923GjCM1LiU-VSc.jpg",
    "auth_date": 1565899537,
    "hash": "3ee3d6b0617dad1b0d42a38126af399e679b8656e2872087e56c83d36c0b45a9",
}
DEFAULT_PASSWORD = "qwe123QWE"
fake_users_dicts = [
    {"login": "admin", "password": DEFAULT_PASSWORD},
    {"login": "user", "password": DEFAULT_PASSWORD},
    {"login": "wheelov", "password": DEFAULT_PASSWORD},
]
question_create_dict = {
    "question": "How are you?",
    "response": 1,
    "answer1": "I'm fine. Thank you!",
    "answer2": "So so",
    "answer3": "Marvellous my friend",
    "answer4": "Simply awesome!"
}
question_update_dict = {
    "question": "How are you?",
    "response": 3,
    "answer1": "Silence...",
    "answer2": "Thinking about next day",
    "answer3": "Got sick",
    "answer4": "Oh, da hello!"
}
fake_users = [schemas.UserCreate(**user_dict) for user_dict in fake_users_dicts]
ENGINE = create_engine("postgresql://postgres:qwe123QWE@localhost:5432/postgres")
