from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ENGINE = create_engine("postgresql://postgres:qwe123QWE@localhost:5432/postgres")
Session = sessionmaker()
Session.configure(bind=ENGINE)


@contextmanager
def session_scope() -> Session:
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
