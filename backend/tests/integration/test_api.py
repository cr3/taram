"""Integration tests for the API service."""

from hamcrest import (
    assert_that,
    has_entries,
)


def test_api_domains(api_session, unique):
    """The API should expose a domains API."""
    domain = unique("domain")
    api_session.post("/domains", json={"domain": domain, "restart_sogo": False})
    api_session.put(f"/domains/{domain}", json={"description": "test"})
    try:
        response = api_session.get(f"/domains/{domain}")
    finally:
        api_session.delete(f"/domains/{domain}")

    assert_that(response.json(), has_entries(domain=domain, description="test"))
