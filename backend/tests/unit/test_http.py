"""Unit tests for the http module."""

import pytest
import responses

from taram.http import (
    HTTP_METHODS,
    HTTPSession,
)


@responses.activate
@pytest.mark.parametrize("method", HTTP_METHODS)
def test_http_session_request(method):
    """The HTTP session request should append the path to the base URL."""
    responses.add(
        method,
        "http://localhost/a",
        status=200,
    )

    session = HTTPSession("http://localhost/")
    result = session.request(method, "a")
    assert result.status_code == 200


@responses.activate
def test_http_session_get():
    """The HTTP session should map methods to request."""
    responses.add(
        responses.GET,
        "http://localhost/a",
        status=200,
    )

    session = HTTPSession("http://localhost/")
    result = session.get("a")
    assert result.status_code == 200
