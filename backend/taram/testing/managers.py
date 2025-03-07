"""Manager fixtures."""

from unittest.mock import Mock

import pytest

from taram.domain import DomainManager
from taram.mailbox import MailboxManager
from taram.sogo import Sogo


@pytest.fixture
def domain_manager(db_session):
    """Domain manager fixture."""
    dockerapi_session = Mock()
    return DomainManager(db_session, dockerapi_session)


@pytest.fixture
def mailbox_manager(db_session):
    """Mailbox manager fixture."""
    sogo = Sogo(db_session, Mock())
    return MailboxManager(db_session, sogo)
