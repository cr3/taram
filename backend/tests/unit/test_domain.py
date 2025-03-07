"""Unit tests for the domain module."""

import pytest

from taram.models import (
    AliasDomainModel,
    DomainModel,
)
from taram.schemas import (
    DomainCreate,
    DomainUpdate,
)


def test_domain_manager_get_origin_domain_without_alias(domain_manager, db_session, unique):
    """Getting an origin domain without an alias should return the domain."""
    domain = unique("domain")
    result = domain_manager.get_origin_domain(domain)
    assert result == domain


def test_domain_manager_get_origin_domain_with_alias(domain_manager, db_model, db_session, unique):
    """Getting an origin domain with an alias should return the alias."""
    alias_domain, target_domain = unique("domain"), unique("domain")
    db_model(AliasDomainModel, alias_domain=alias_domain, target_domain=target_domain)
    result = domain_manager.get_origin_domain(alias_domain)
    assert result == target_domain


def test_domain_manager_get_domain_details(db_model, db_session, domain_manager, unique):
    """Getting domain details should at least include the domain name."""
    domain = unique("domain")
    db_model(DomainModel, domain=domain)
    result = domain_manager.get_domain_details(domain)
    assert result.domain == domain


def test_domain_manager_create_domain(db_session, domain_manager, unique):
    """Getting domain templates should return at least one template."""
    domain = unique("domain")
    domain_create = DomainCreate(domain=domain)
    domain_manager.create_domain(domain_create)
    domain_manager.dockerapi_session.post.assert_called_once_with("/services/sogo/restart")

    db_session.flush()
    result = domain_manager.get_domain_details(domain)
    assert result.domain == domain


def test_domain_manager_update_domain(db_model, db_session, domain_manager, unique):
    """Updating a domain should return the updated details."""
    domain = unique("domain")
    db_model(DomainModel, domain=domain)
    domain_update = DomainUpdate(active=False)
    result = domain_manager.update_domain(domain, domain_update)
    assert result.active is False


def test_domain_manager_delete_domain(db_model, db_session, domain_manager, unique):
    """Deleting a domain should delete it from everywhere."""
    domain = unique("domain")
    db_model(DomainModel, domain=domain)
    domain_manager.delete_domain(domain)
    with pytest.raises(KeyError):
        domain_manager.get_domain_details(domain)
