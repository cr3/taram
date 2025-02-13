"""Unit tests for the cli module."""

from unittest.mock import Mock, patch

import pytest
import responses

from taram.cli import (
    API_URL,
    call_api,
    get_arg_type,
    get_openapi_schema,
    main,
    make_args_parser,
)
from taram.http import HTTPSession


@pytest.mark.parametrize(
    "arg, expected",
    [
        ("boolean", bool),
        ("integer", int),
        ("number", float),
        ("string", str),
        ("test", str),
    ],
)
def test_get_arg_type(arg, expected):
    result = get_arg_type(arg)
    assert result == expected


def test_get_openapi_schema():
    """Getting the OpenAPI schema should return the body of openapi.json."""
    body = {"test": True}
    http_session = HTTPSession("http://localhost/")
    with patch.object(http_session, "get") as mock_get:
        mock_get.return_value = Mock(json=Mock(return_value=body))
        result = get_openapi_schema(http_session)

    assert result == body


def test_call_api():
    """Calling the API sould make a request with the given method."""
    body = {"test": True}
    http_session = HTTPSession("http://localhost/")
    with patch.object(http_session, "request") as mock_request:
        mock_request.return_value = Mock(json=Mock(return_value=body))
        result = call_api(http_session, "GET", "/test", {}, {})

    assert result == body


def test_make_args_parser_command():
    """Making an args parser should parse commands from the schema."""
    args_parser = make_args_parser({
        "paths": {
            "test": {
                "get": {},
            },
        },
    })
    args = args_parser.parse_args(["get_test"])
    assert args.command == "get_test"


def test_make_args_parser_command_error(capsys, unique):
    """Making an args parser should raise on unknown commands."""
    args_parser = make_args_parser({})
    with pytest.raises(SystemExit):
        args_parser.parse_args(["get_test"])


@responses.activate
def test_main_help(capsys):
    """The main function should output usage when asked for --help."""
    responses.add(
        responses.GET,
        f"{API_URL}openapi.json",
        json={},
    )
    with pytest.raises(SystemExit):
        main(["--help"])

    captured = capsys.readouterr()
    assert "usage" in captured.out
