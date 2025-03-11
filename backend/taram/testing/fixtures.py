"""Testing fixtures."""

import logging
import os
from unittest.mock import patch

import pytest

from taram.logger import setup_logger
from taram.testing.logger import LoggerHandler


@pytest.fixture
def api_app(db_session):
    from fastapi.testclient import TestClient

    from taram.api import app
    from taram.db import get_db_session

    def override_get_db_session():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db_session] = override_get_db_session

    env = {
        "DBDRIVER": "sqlite",
        "DBNAME": ":memory:",
    }
    with patch.dict(os.environ, env), TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def logger_handler():
    """Logger handler fixture."""
    handler = LoggerHandler()
    setup_logger(logging.DEBUG, handler)
    try:
        yield handler
    finally:
        setup_logger()
