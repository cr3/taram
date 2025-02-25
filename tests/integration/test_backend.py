"""Integration tests for the backend service."""

from hamcrest import (
    assert_that,
    has_entries,
)


def test_backend_domains(backend_session, unique):
    """The backend should expose a domains API."""
    domain = unique("domain")
    backend_session.post("/domains", json={"domain": domain})
    backend_session.put(f"/domains/{domain}", json={"description": "test"})
    response = backend_session.get(f"/domains/{domain}")
    backend_session.delete(f"/domains/{domain}")
    assert_that(response.json(), has_entries(domain=domain, description="test"))
