"""Unit tests for the api module."""

from hamcrest import (
    assert_that,
    has_entries,
    has_item,
)

from taram.models import (
    DomainModel,
    MailboxModel,
)


def test_api_get_domains(db_model, api_app):
    """Getting domains should return the list of domains."""
    domain_model = db_model(DomainModel)
    response = api_app.get("/domains")
    assert_that(response.json(), has_item(domain_model.domain))


def test_api_post_domains(db_model, api_app, unique):
    """Posting a domain should create the domain in the api."""
    domain = unique("domain")
    api_app.post("/domains", json={
        "domain": domain,
        "restart_sogo": False,
    })
    response = api_app.get(f"/domains/{domain}")
    assert response.status_code == 200


def test_api_put_domain(db_model, api_app):
    """Putting a domain should update it from the attributes."""
    domain_model = db_model(DomainModel, description="old")
    api_app.put(f"/domains/{domain_model.domain}", json={"description": "new"})
    response = api_app.get(f"/domains/{domain_model.domain}")
    assert_that(response.json(), has_entries(description="new"))


def test_api_delete_domain(api_app, unique):
    """Deleting a domain should delete it from the list of domains."""
    domain = unique("domain")
    api_app.post("/domains", json={
        "domain": domain,
        "restart_sogo": False,
    })
    api_app.delete(f"/domains/{domain}")
    response = api_app.get(f"/domains/{domain}")
    assert response.status_code == 404


def test_api_get_mailboxes(db_model, api_app):
    """Getting mailboxes should return the list of mailboxes."""
    mailbox_model = db_model(MailboxModel)
    response = api_app.get("/mailboxes")
    assert_that(response.json(), has_item(mailbox_model.username))


def test_api_post_mailboxes(db_model, api_app, unique):
    """Posting a mailbox should create the mailbox in the api."""
    local_part = unique("text")
    domain = unique("domain")
    password = unique("password")
    username = f"{local_part}@{domain}"
    api_app.post("/domains", json={
        "domain": domain,
        "restart_sogo": False,
    })
    api_app.post("/mailboxes", json={
        "local_part": local_part,
        "domain": domain,
        "password": password,
        "password2": password,
    })
    response = api_app.get(f"/mailboxes/{username}")
    assert response.status_code == 200
