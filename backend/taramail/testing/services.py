"""Service fixtures."""

from functools import partial
from pathlib import Path

import pytest

from taramail.http import HTTPSession
from taramail.testing.compose import ComposeServer


@pytest.fixture(scope="session")
def project():
    return "test"


@pytest.fixture(scope="session")
def env_vars(project):
    """Environment variables for the services.

    Static because they are persisted in volumes, e.g. mysql-vol-1.
    """
    return {
        "COMPOSE_PROJECT_NAME": project,
        "DBDRIVER": "mysql",
        "DBNAME": "test",
        "DBUSER": "test",
        "DBPASS": "test",
        "DBROOT": "test",
        "SKIP_FTS": "y",
        "REDISPASS": "test",
        "MAIL_HOSTNAME": "test.local",
    }


@pytest.fixture(scope="session")
def env_file(env_vars, request):
    """Environment file containing `env_vars`.

    Cached for troubleshooting purposes.
    """
    env_file = request.config.cache.makedir("compose") / "env"
    with env_file.open("w") as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")

    return env_file


@pytest.fixture(scope="session")
def compose_files(request):
    directory = Path(request.config.rootdir)
    filenames = ["docker-compose.yml", "compose.yaml", "compose.yml"]
    while True:
        for filename in filenames:
            path = directory / filename
            if path.exists():
                return list(directory.glob(f"{path.stem}.*"))

        if directory == directory.parent:
            raise KeyError("Docker compose file not found")

        directory = directory.parent


@pytest.fixture(scope="session")
def compose_server(project, env_file, compose_files, process):
    return partial(
        ComposeServer,
        project=project,
        env_file=env_file,
        compose_files=compose_files,
        process=process,
    )


@pytest.fixture(scope="session")
def api_service(compose_server):
    """API service fixture."""
    server = compose_server("Uvicorn running on")
    with server.run("api") as service:
        yield service


@pytest.fixture(scope="session")
def api_session(api_service):
    """API HTTP session to the service fixture."""
    return HTTPSession.with_origin(f"http://{api_service.ip}/")


@pytest.fixture(scope="session")
def clamd_service(compose_server):
    """Clamd service fixture."""
    server = compose_server("socket found, clamd started")
    with server.run("clamd") as service:
        yield service


@pytest.fixture(scope="session")
def dockerapi_service(compose_server):
    """Dockerapi service fixture."""
    server = compose_server("Uvicorn running on")
    with server.run("dockerapi") as service:
        yield service


@pytest.fixture(scope="session")
def dockerapi_session(dockerapi_service):
    """Dockerapi HTTP session to the service fixture."""
    return HTTPSession.with_origin(f"http://{dockerapi_service.ip}/")


@pytest.fixture(scope="session")
def dovecot_service(compose_server, ssl_dir):
    """Dovecot service fixture."""
    server = compose_server("dovecot entered RUNNING state")
    with server.run("dovecot") as service:
        yield service


@pytest.fixture(scope="session")
def frontend_service(compose_server):
    """Frontend service fixture."""
    server = compose_server("ready")
    with server.run("frontend") as service:
        yield service


@pytest.fixture(scope="session")
def memcached_service(compose_server):
    """Memcached service fixture."""
    server = compose_server("server listening")
    with server.run("memcached") as service:
        yield service


@pytest.fixture(scope="session")
def mysql_service(compose_server):
    """MySQL service fixture."""
    server = compose_server("mysqld: ready for connections")
    with server.run("mysql") as service:
        yield service


@pytest.fixture(scope="session")
def postfix_service(compose_server):
    """Postfix service fixture."""
    server = compose_server("starting the Postfix mail system")
    with server.run("postfix") as service:
        yield service


@pytest.fixture(scope="session")
def redis_service(compose_server):
    """Redis service fixture."""
    server = compose_server("Ready to accept connections tcp")
    with server.run("redis") as service:
        yield service


@pytest.fixture(scope="session")
def redis_client(redis_service, env_vars):
    """Redis client to the service fixture."""
    from redis import StrictRedis

    return StrictRedis(
        host=redis_service.ip,
        port=6379,
        decode_responses=True,
        db=0,
        password=env_vars["REDISPASS"],
    )


@pytest.fixture(scope="session")
def rspamd_service(redis_service, compose_server):
    """Rspamd service fixture."""
    server = compose_server("listening for control commands")
    with server.run("rspamd") as service:
        yield service


@pytest.fixture(scope="session")
def sogo_service(redis_service, compose_server):
    """SOGo service fixture."""
    server = compose_server("notified the watchdog that we are ready")
    with server.run("sogo") as service:
        yield service


@pytest.fixture(scope="session")
def unbound_service(compose_server):
    """Unbound service fixture."""
    server = compose_server("start of service")
    with server.run("unbound") as service:
        yield service
