"""Integration tests for the frontend service."""

import requests


def test_frontend_service(frontend_service):
    """The frontend home should contain the Taram string."""
    response = requests.get(f"http://{frontend_service.ip}:3000/", timeout=10)

    assert "Taram" in response.text
