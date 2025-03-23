"""Unit testing fixtures."""

import pytest

redis_queue = pytest.fixture(lambda memory_queue: memory_queue)
redis_store = pytest.fixture(lambda memory_store: memory_store)
memcached_store = pytest.fixture(lambda memory_store: memory_store)
