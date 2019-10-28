import getpass

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

IN_GITPOD = True if getpass.getuser() == "gitpod" else False
SQLALCHEMY_DATABASE_URL = (
    "postgresql://postgres:qwe123QWE@localhost:5432/postgres"
    if not IN_GITPOD
    else f"postgresql://gitpod@localhost:5432/postgres"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
