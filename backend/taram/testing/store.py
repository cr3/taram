"""Store fixtures."""

import pytest
from yarl import URL

from taram.store import Store


@pytest.fixture
def memcached_store(memcached_service):
    """Redis store fixture."""
    url = URL.build(
        scheme="memcached",
        host=memcached_service.ip,
        port=11211,
    )
    return Store.from_url(url)


@pytest.fixture
def memory_store():
    """Memory store fixture."""
    return Store.from_url("memory:/")


@pytest.fixture
def redis_store(redis_service):
    """Redis store fixture."""
    url = URL.build(
        scheme="redis",
        host=redis_service.ip,
        port=6379,
        password=redis_service.env["REDISPASS"],
    )
    return Store.from_url(url)


@pytest.fixture(
    params=[
        "memcached_store",
        "memory_store",
        "redis_store",
    ],
)
def store(request):
    """Store fixture."""
    return request.getfixturevalue(request.param)
