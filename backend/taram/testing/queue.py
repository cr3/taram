"""Queue fixtures."""

import pytest
from yarl import URL

from taram.queue import Queue


@pytest.fixture
def memory_queue():
    """Memory queue fixture."""
    url = URL.build(scheme="memory")
    return Queue.from_url(url)


@pytest.fixture
def redis_queue(redis_service, env_vars):
    """Redis queue fixture."""
    url = URL.build(
        scheme="redis",
        host=redis_service.ip,
        port=6379,
        password=env_vars["REDISPASS"],
    )
    return Queue.from_url(url)


@pytest.fixture(
    params=[
        "memory_queue",
        "redis_queue",
    ],
)
def queue(request):
    """Queue fixture."""
    return request.getfixturevalue(request.param)
