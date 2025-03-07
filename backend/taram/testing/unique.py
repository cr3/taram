"""Unique fixtures for data generation."""

from datetime import UTC, datetime
from functools import partial
from secrets import choice

from sqlalchemy.types import (
    Boolean,
    DateTime,
    Enum,
    Integer,
    LargeBinary,
    String,
)


def unique_db_model(unique, model, **data):
    """Make a unique database model."""
    # Only make values for columns that absolutely need a value.
    for column in model.__table__.columns:
        if not (column.nullable or column.default or column.server_default):
            data.setdefault(column.name, unique("db-value", column.type))

    return model(**data)


def unique_db_value(unique, column_type):
    """Make a unique database value given a type."""
    for value_type, value_factory in [
        (Boolean, lambda: True),
        (DateTime, datetime.now(UTC)),
        (Enum, lambda: choice(list(column_type.enum_class))),
        (Integer, partial(unique, "integer")),
        (LargeBinary, partial(unique, "bytes")),
        (String, partial(unique, "text")),
    ]:
        if isinstance(column_type, value_type):
            return value_factory()

    raise ValueError(f"Column type {column_type!r} not supported")


def unique_domain(unique, tld="com"):
    """Returns a domain unique to this factory instance."""
    suffix = f".{tld}"
    return unique("text", separator="", suffix=suffix)
