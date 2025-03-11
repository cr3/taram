"""Unit testing fixtures."""

import pytest

store = pytest.fixture(lambda memory_store: memory_store)
