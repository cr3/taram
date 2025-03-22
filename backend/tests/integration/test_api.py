"""Integration tests for the API service."""

from hamcrest import (
    assert_that,
    has_entries,
)


def test_api_domains(api_session, unique):
    """The API should expose a domains API."""
    domain = unique("domain")
    api_session.post("/domains", json={
        "domain": domain,
        "restart_sogo": False,
    })
    api_session.put(f"/domains/{domain}", json={"description": "test"})
    try:
        response = api_session.get(f"/domains/{domain}")
    finally:
        api_session.delete(f"/domains/{domain}")

    assert_that(response.json(), has_entries(domain=domain, description="test"))


def test_api_mailboxes(api_session, unique):
    """The API should expose a mailboxes API."""
    local_part = unique("text")
    domain = unique("domain")
    password = unique("password")
    username = f"{local_part}@{domain}"
    api_session.post("/domains", json={
        "domain": domain,
        "restart_sogo": False,
    })
    api_session.post("/mailboxes", json={
        "local_part": local_part,
        "domain": domain,
        "password": password,
        "password2": password,
    })
    api_session.put(f"/mailboxes/{username}", json={"name": "test"})
    try:
        response = api_session.get(f"/mailboxes/{username}")
    finally:
        api_session.delete(f"/domains/{username}")

    assert_that(response.json(), has_entries(username=username, name="test"))
