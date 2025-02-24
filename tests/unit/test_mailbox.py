"""Unit tests for the mailbox module."""

import pytest

from taram.models import (
    MailboxModel,
    UserAttributesModel,
)
from taram.schemas import (
    DomainCreate,
    MailboxCreate,
    MailboxUpdate,
)


@pytest.fixture
def domain(db_session, domain_manager, unique):
    """Return the domain name for a managed domain."""
    domain = unique("domain")
    domain_create = DomainCreate(domain=domain)
    domain_manager.create_domain(domain_create)
    db_session.flush()

    return domain


def test_mailbox_manager_get_mailbox_details(db_session, domain, mailbox_manager):
    """Getting mailbox details should at least include the local part."""
    mailbox_create = MailboxCreate(
        local_part="a",
        domain=domain,
        password="x",  # noqa: S106
        password2="x",
    )
    mailbox = mailbox_manager.create_mailbox(mailbox_create)
    db_session.flush()

    result = mailbox_manager.get_mailbox_details(mailbox.username)
    assert result.local_part == "a"


def test_mailbox_manager_create_mailbox(db_session, domain, mailbox_manager):
    """Creating a mailbox should create a mailbox row."""
    mailbox_create = MailboxCreate(
        local_part="a",
        domain=domain,
        password="x",  # noqa: S106
        password2="x",
    )
    mailbox_manager.create_mailbox(mailbox_create)
    db_session.flush()

    result = db_session.query(MailboxModel).filter_by(domain=domain).one()
    assert result.domain == domain


def test_mailbox_manager_update_mailbox(db_session, domain, mailbox_manager):
    """Updating a mailbox should return the updated details."""
    mailbox_create = MailboxCreate(
        local_part="a",
        domain=domain,
        password="x",  # noqa: S106
        password2="x",
    )
    mailbox = mailbox_manager.create_mailbox(mailbox_create)
    db_session.flush()

    mailbox_update = MailboxUpdate(name="b")
    result = mailbox_manager.update_mailbox(mailbox.username, mailbox_update)
    assert result.name == "b"


def test_mailbox_manager_update_mailbox_attributes(db_session, domain, mailbox_manager):
    """Updating mailbox attributes should update the user attributes."""
    mailbox_create = MailboxCreate(
        local_part="a",
        domain=domain,
        password="x",  # noqa: S106
        password2="x",
    )
    mailbox = mailbox_manager.create_mailbox(mailbox_create)
    db_session.flush()

    mailbox_update = MailboxUpdate(sogo_access=False)
    mailbox_manager.update_mailbox(mailbox.username, mailbox_update)
    result = db_session.query(UserAttributesModel).filter_by(username=mailbox.username).one()
    assert result.sogo_access is False
