"""Integration tests for the rspamd service."""

from textwrap import dedent

import requests


def test_rspamd_service(rspamd_service):
    """The score for emails from monit@localhost should be 9999."""
    email = dedent("""\
        To: null@localhost
        From: monit@localhost

        Empty
    """)
    response = requests.post(f"http://{rspamd_service.ip}:11333/scan", data=email, timeout=10)

    assert response.json()["default"]["required_score"] == 9999.0
