"""Service fixtures."""

import os
from tempfile import NamedTemporaryFile
from textwrap import dedent

import pytest

from taram.http import HTTPSession
from taram.testing.compose import ComposeServer


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


@pytest.fixture(scope="session")
def backend_service(env_file, project, process):
    """Backend service fixture."""
    server = ComposeServer(
        "Uvicorn running on",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("backend") as service:
        yield service


@pytest.fixture(scope="session")
def backend_session(backend_service):
    """Backend HTTP session to the service fixture."""
    return HTTPSession.with_origin(f"http://{backend_service.ip}/")


@pytest.fixture(scope="session")
def clamd_service(project, process):
    """Clamd service fixture."""
    server = ComposeServer(
        "socket found, clamd started",
        project=project,
        process=process,
    )
    with server.run("clamd") as service:
        yield service


@pytest.fixture(scope="session")
def dockerapi_service(env_file, project, process):
    """Dockerapi service fixture."""
    server = ComposeServer(
        "Uvicorn running on",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("dockerapi") as service:
        yield service


@pytest.fixture(scope="session")
def dockerapi_session(dockerapi_service):
    """Dockerapi HTTP session to the service fixture."""
    return HTTPSession.with_origin(f"http://{dockerapi_service.ip}/")


@pytest.fixture(scope="session")
def dovecot_service(env_file, project, process):
    """Dovecot service fixture."""
    server = ComposeServer(
        "dovecot entered RUNNING state",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("dovecot") as service:
        yield service


@pytest.fixture(scope="session")
def memcached_service(env_file, project, process):
    """Memcached service fixture."""
    server = ComposeServer(
        "server listening",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("memcached") as service:
        yield service


@pytest.fixture(scope="session")
def mysql_service(env_file, project, process):
    """MySQL service fixture."""
    server = ComposeServer(
        "mysqld: ready for connections",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("mysql") as service:
        yield service


@pytest.fixture(scope="session")
def postfix_service(env_file, project, process):
    """Postfix service fixture."""
    server = ComposeServer(
        "starting the Postfix mail system",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("postfix") as service:
        yield service


@pytest.fixture(scope="session")
def redis_service(env_file, project, process):
    """Redis service fixture."""
    server = ComposeServer(
        "Ready to accept connections tcp",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("redis") as service:
        yield service


@pytest.fixture(scope="session")
def redis_client(redis_service):
    """Redis client to the service fixture."""
    from redis import StrictRedis

    return StrictRedis(
        host=redis_service.ip,
        port=6379,
        decode_responses=True,
        db=0,
        password=redis_service.env["REDISPASS"],
    )


@pytest.fixture(scope="session")
def rspamd_service(redis_service, env_file, project, process):
    """Rspamd service fixture."""
    server = ComposeServer(
        "listening for control commands",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("rspamd") as service:
        yield service


@pytest.fixture(scope="session")
def sogo_service(redis_service, env_file, project, process):
    """SOGo service fixture."""
    server = ComposeServer(
        "notified the watchdog that we are ready",
        env_file=env_file,
        project=project,
        process=process,
    )
    with server.run("sogo") as service:
        yield service


@pytest.fixture(scope="session")
def unbound_service(project, process):
    """Unbound service fixture."""
    server = ComposeServer(
        "start of service",
        project=project,
        process=process,
    )
    with server.run("unbound") as service:
        yield service
