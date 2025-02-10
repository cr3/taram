"""Taram database fixtures."""

import pytest
from attr import define, field
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from taram.models import SQLModel


def pytest_addoption(parser):
    parser.addoption(
        "--db-url",
        action="store",
        default="sqlite:///:memory:",
        help="Database URL to use for tests.",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    db_url = session.config.getoption("--db-url")
    try:
        # Attempt to create an engine and connect to the database.
        engine = create_engine(
            db_url,
            poolclass=StaticPool,
        )
        connection = engine.connect()
        # Close the connection right after a successful connect.
        connection.close()
    except OperationalError as e:
        pytest.exit(f"Failed to connect to the database at {db_url}: {e}")


@pytest.fixture(scope="session")
def db_url(request):
    """Fixture to get the database URL."""
    return request.config.getoption("--db-url")


@pytest.fixture(scope="session")
def db_engine(db_url):
    """Create a SQLAlchemy engine."""
    connect_args = {"check_same_thread": False}
    engine = create_engine(db_url, connect_args=connect_args)
    SQLModel.metadata.create_all(engine)
    try:
        yield engine
    finally:
        SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session with a rollback at the end of the test."""
    # Create a sessionmaker to manage sessions
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    # Create tables in the database
    connection = db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@define(frozen=True)
class DbModel:
    """Fixture for adding unique models to the database."""

    session = field()
    unique = field()

    def __call__(self, model, **kwargs):
        """Make a unique model and add it to the database.

        This also happens to flush the database session so that the
        default and server_default values can be realized.
        """
        kwargs = self._ensure_foreign_keys_exist(model, kwargs)

        obj = self.unique("db-model", model, **kwargs)
        self.session.add(obj)
        self.session.flush()

        return obj

    def _ensure_foreign_keys_exist(self, model, kwargs):
        """Make sure model can be created by pre-creating foreign objects."""
        new_kwargs = kwargs.copy()

        ignored_fkeys = self._relationship_covered_keys(model, kwargs) + list(kwargs.keys())

        for fkey_constraint in model.__table__.foreign_key_constraints:
            if not self._applicable(fkey_constraint, ignored_fkeys):
                continue

            table = fkey_constraint.referred_table
            foreign_model = self._get_model_by_table_name(model, table.name)
            foreign_object = self(foreign_model)

            # Kwargs must reference the new foreign object
            for local_key, remote_key in zip(fkey_constraint.column_keys, fkey_constraint.elements):
                new_kwargs[local_key] = getattr(foreign_object, remote_key.column.name)

        return new_kwargs

    def _applicable(self, fkey_constraint, ignored_fkeys):
        # Skip nullable columns
        if all(col.nullable for col in fkey_constraint.columns):
            return False

        # Ignore manually set and relationship covered keys, the existance
        # of the foreign object is the caller's responsibility
        return all(col.name not in ignored_fkeys for col in fkey_constraint.columns)

    def _relationship_covered_keys(self, model, kwargs):
        """Find columns covered by relationships.

        To avoid create a foreign instance one is already passed as a
        relationship.
        """
        ignored_fkeys = []

        for relationship in model.__mapper__.relationships:
            if relationship.key in kwargs:
                ignored_fkeys += [c.name for c in relationship.local_columns]

        return ignored_fkeys

    def _get_model_by_table_name(self, model, table_name):
        for mapper in model.registry.mappers:
            if getattr(mapper.class_, "__tablename__", None) == table_name:
                return mapper.class_

        raise ValueError(f"Table {table_name!r} not found in registry.")


@pytest.fixture(scope="function")
def db_model(db_session, unique):
    """Database model fixture."""
    return DbModel(db_session, unique)
