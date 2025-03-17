"""Database functions."""

import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import sessionmaker


def get_db_url(env=os.environ) -> URL:
    """Return a database URL from DB variables in the environment."""
    return URL.create(
        drivername=env["DBDRIVER"],
        username=env.get("DBUSER"),
        password=env.get("DBPASS"),
        host=env.get("DBHOST"),
        port=env.get("DBPORT"),
        database=env.get("DBNAME"),
    )


@contextmanager
def get_db_session(env=os.environ) -> Iterator[DBSession]:
    """Yield a database session."""
    url = get_db_url(env)
    engine = create_engine(url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@contextmanager
def db_transaction(db: DBSession) -> Iterator[DBSession]:
    """Context manager for handling database transactions safely."""
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
