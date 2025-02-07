"""Taram fixtures."""

import logging
import os
from tempfile import NamedTemporaryFile
from textwrap import dedent
from unittest.mock import patch

import pytest

from taram.logger import setup_logger
from taram.testing.compose import ComposeServer
from taram.testing.logger import LoggerHandler


@pytest.fixture(scope="session")
def project():
    return "test"


@pytest.fixture(scope="session")
def env_file(project):
    # These must be static because they are persisted in mysql-vol-1.
    with NamedTemporaryFile(delete=False) as tmp:
        tmp.write(dedent(f"""\
            COMPOSE_PROJECT_NAME={project}
            DBDRIVER=mysql
            DBNAME=test
            DBUSER=test
            DBPASS=test
            DBROOT=test
            REDISPASS=test
            MAIL_HOSTNAME=test.local
        """).encode())
        tmp.close()

        try:
            yield tmp.name
        finally:
            os.unlink(tmp.name)


@pytest.fixture
def backend_app(db_session, project):
    from fastapi.testclient import TestClient

    from taram.backend import app
    from taram.db import get_session

    def override_get_session():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_session] = override_get_session

    env = {
        "DBDRIVER": "sqlite",
        "DBNAME": ":memory:",
    }
    with patch.dict(os.environ, env), TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def backend_client(env_file, project, process):
    """Backend client fixture."""
    server = ComposeServer(
        "Uvicorn running on",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("backend") as client:
        yield client


@pytest.fixture(scope="session")
def clamd_client(project, process):
    """Clamd client fixture."""
    server = ComposeServer(
        "socket found, clamd started",
        project=project,
        process=process,
    )
    with server.run("clamd") as client:
        yield client


@pytest.fixture
def dockerapi_app(project):
    from fastapi.testclient import TestClient

    from taram.dockerapi import app

    env = {
        "COMPOSE_PROJECT_NAME": project,
    }
    with patch.dict(os.environ, env), TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def dockerapi_client(env_file, project, process):
    """Dockerapi client fixture."""
    server = ComposeServer(
        "Uvicorn running on",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("dockerapi") as client:
        yield client


@pytest.fixture(scope="session")
def dovecot_client(env_file, project, process):
    """Dovecot client fixture."""
    server = ComposeServer(
        "dovecot entered RUNNING state",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("dovecot") as client:
        yield client


@pytest.fixture(scope="session")
def memcached_client(env_file, project, process):
    """Memcached client fixture."""
    server = ComposeServer(
        "server listening",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("memcached") as client:
        yield client


@pytest.fixture(scope="session")
def mysql_client(env_file, project, process):
    """MySQL client fixture."""
    server = ComposeServer(
        "mysqld: ready for connections",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("mysql") as client:
        yield client


@pytest.fixture(scope="session")
def postfix_client(env_file, project, process):
    """Postfix client fixture."""
    server = ComposeServer(
        "starting the Postfix mail system",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("postfix") as client:
        yield client


@pytest.fixture(scope="session")
def redis_client(env_file, project, process):
    """Redis client fixture."""
    from redis import StrictRedis

    server = ComposeServer(
        "Ready to accept connections tcp",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("redis") as client:
        redis = StrictRedis(
            host=client.ip,
            port=6379,
            decode_responses=True,
            db=0,
            password=client.env["REDISPASS"],
        )
        yield redis


@pytest.fixture(scope="session")
def rspamd_client(redis_client, env_file, project, process):
    """Rspamd client fixture."""
    server = ComposeServer(
        "listening for control commands",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("rspamd") as client:
        yield client


@pytest.fixture(scope="session")
def sogo_client(redis_client, env_file, project, process):
    """SOGo client fixture."""
    server = ComposeServer(
        "notified the watchdog that we are ready",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("sogo") as client:
        yield client


@pytest.fixture(scope="session")
def unbound_client(project, process):
    """Unbound client fixture."""
    server = ComposeServer(
        "start of service",
        project=project,
        process=process,
    )
    with server.run("unbound") as client:
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
