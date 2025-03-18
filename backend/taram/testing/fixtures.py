"""Testing fixtures."""

import logging
import os
from subprocess import check_call
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from taram.api import (
    app,
    get_domain_manager,
    get_mailbox_manager,
)
from taram.logger import setup_logger
from taram.testing.logger import LoggerHandler


@pytest.fixture
def api_app(db_session, domain_manager, mailbox_manager):

    async def override_get_domain_manager():
        yield domain_manager

    async def override_get_mailbox_manager():
        yield mailbox_manager

    app.dependency_overrides[get_domain_manager] = override_get_domain_manager
    app.dependency_overrides[get_mailbox_manager] = override_get_mailbox_manager

    url = db_session.bind.engine.url
    env = {
        "DBDRIVER": url.drivername,
        "DBNAME": url.database,
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


@pytest.fixture(scope="session")
def ssl_dir(request, env_file):
    """Fixture to get the SSL directory."""
    backend_root = request.config.rootpath
    project_root = backend_root.parent
    check_call(["make", "-C", project_root, f"ENV={env_file}", "ssl"])  # noqa: S603, S607
    return project_root / "ssl"
