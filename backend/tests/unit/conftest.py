"""Unit testing fixtures."""

import pytest

redis_store = pytest.fixture(lambda memory_store: memory_store)
memcached_store = pytest.fixture(lambda memory_store: memory_store)
