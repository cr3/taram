"""Unit tests for the mailbox module."""

import pytest

from taram.schemas import (
    DomainCreate,
    MailboxCreate,
    MailboxUpdate,
)


@pytest.fixture
def domain(domain_manager, unique):
    """Return the domain name for a managed domain."""
    domain = unique("domain")
    domain_create = DomainCreate(domain=domain)
    domain_manager.create_domain(domain_create)
    domain_manager.db.flush()

    return domain


def test_mailbox_manager_get_mailbox_details(domain, mailbox_manager):
    """Getting mailbox details should at least include the local part."""
    mailbox_create = MailboxCreate(
        local_part="a",
        domain=domain,
        password="x",
        password2="x",
    )
    mailbox = mailbox_manager.create_mailbox(mailbox_create)
    mailbox_manager.db.flush()

    result = mailbox_manager.get_mailbox_details(mailbox.username)
    assert result.local_part == "a"


def test_mailbox_manager_create_mailbox(domain, mailbox_manager):
    """Creating a mailbox should create a mailbox row."""
    mailbox_create = MailboxCreate(
        local_part="a",
        domain=domain,
        password="x",
        password2="x",
    )
    mailbox_manager.create_mailbox(mailbox_create)
    mailbox_manager.db.flush()

    result = mailbox_manager.get_mailbox_details(f"a@{domain}")
    assert result.domain == domain


def test_mailbox_manager_update_mailbox(domain, mailbox_manager):
    """Updating a mailbox should return the updated details."""
    mailbox_create = MailboxCreate(
        local_part="a",
        domain=domain,
        password="x",
        password2="x",
    )
    mailbox = mailbox_manager.create_mailbox(mailbox_create)
    mailbox_manager.db.flush()

    mailbox_update = MailboxUpdate(name="b")
    result = mailbox_manager.update_mailbox(mailbox.username, mailbox_update)
    assert result.name == "b"


def test_mailbox_manager_update_mailbox_attributes(domain, mailbox_manager):
    """Updating mailbox attributes should update the user attributes."""
    mailbox_create = MailboxCreate(
        local_part="a",
        domain=domain,
        password="x",
        password2="x",
    )
    mailbox = mailbox_manager.create_mailbox(mailbox_create)
    mailbox_manager.db.flush()

    mailbox_update = MailboxUpdate(sogo_access=False)
    mailbox_manager.update_mailbox(mailbox.username, mailbox_update)
    result = mailbox_manager.get_mailbox_details(mailbox.username)
    assert result.sogo_access is False


def test_mailox_manager_delete_mailbox(domain, mailbox_manager):
    """Deleting a domain should delete it from everywhere."""
    mailbox_create = MailboxCreate(
        local_part="a",
        domain=domain,
        password="x",
        password2="x",
    )
    mailbox = mailbox_manager.create_mailbox(mailbox_create)
    mailbox_manager.db.flush()

    mailbox_manager.delete_mailbox(f"a@{domain}")
    with pytest.raises(KeyError):
        mailbox_manager.get_mailbox_details(mailbox.username)
