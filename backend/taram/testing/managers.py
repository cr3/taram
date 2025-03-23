"""Manager fixtures."""

from unittest.mock import Mock

import pytest

from taram.domain import DomainManager
from taram.mailbox import MailboxManager
from taram.sogo import Sogo


@pytest.fixture
def sogo(db_session, memcached_store):
    """Sogo fixture."""
    return Sogo(db_session, memcached_store)


@pytest.fixture
def domain_manager(db_session, redis_store):
    """Domain manager fixture."""
    dockerapi = Mock()
    return DomainManager(db_session, redis_store, dockerapi)


@pytest.fixture
def mailbox_manager(db_session, redis_store, sogo):
    """Mailbox manager fixture."""
    return MailboxManager(db_session, redis_store, sogo)
