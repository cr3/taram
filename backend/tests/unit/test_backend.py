"""Unit tests for the backend module."""

from hamcrest import (
    assert_that,
    has_entries,
    has_item,
)

from taram.models import DomainModel


def test_backend_get_domains(db_model, backend_app):
    """Getting domains should return the list of domains."""
    domain_model = db_model(DomainModel)
    response = backend_app.get("/domains")
    assert_that(response.json(), has_item(domain_model.domain))


def test_backend_post_domains(db_model, backend_app):
    """Posting a domain should create the domain in the backend."""
    domain_model = db_model(DomainModel)
    response = backend_app.get(f"/domains/{domain_model.domain}")
    assert response.status_code == 200


def test_backend_put_domain(db_model, backend_app):
    """Putting a domain should update it from the attributes."""
    domain_model = db_model(DomainModel, description="old")
    backend_app.put(f"/domains/{domain_model.domain}", json={"description": "new"})
    response = backend_app.get(f"/domains/{domain_model.domain}")
    assert_that(response.json(), has_entries(description="new"))


def test_backend_delete_domain(backend_app):
    """Deleting a domain should delete it from the list of domains."""
    domain = "a.com"
    backend_app.post("/domains", json={"domain": domain, "restart_sogo": False})
    backend_app.delete(f"/domains/{domain}")
    response = backend_app.get(f"/domains/{domain}")
    assert response.status_code == 404
