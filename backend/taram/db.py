"""Database functions."""

import os

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session


def get_url(env=os.environ):
    """Return a database URL from DB variables in the environment."""
    return URL.create(
        drivername=env["DBDRIVER"],
        username=env.get("DBUSER"),
        password=env.get("DBPASS"),
        host=env.get("DBHOST"),
        port=env.get("DBPORT"),
        database=env.get("DBNAME"),
    )


def get_session(env=os.environ):
    """Yield a database session."""
    url = get_url(env)
    engine = create_engine(url)
    with Session(engine) as session:
        yield session
