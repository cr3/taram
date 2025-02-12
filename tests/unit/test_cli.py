"""Unit tests for the cli module."""

import pytest
import responses
from requests import HTTPError

from taram.cli import (
    call_api,
    get_arg_type,
    get_openapi_schema,
    main,
    make_args_parser,
)


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


@responses.activate
def test_get_openapi_schema_success():
    """Getting the OpenAPI schema should return the body of openapi.json."""
    body = {"test": True}
    responses.add(
        responses.GET,
        "http://localhost/openapi.json",
        json=body,
        status=200,
    )
    result = get_openapi_schema("http://localhost")
    assert result == body


@responses.activate
def test_get_openapi_schema_error():
    """Getting the OpenAPI schema should raise on error."""
    responses.add(
        responses.GET,
        "http://localhost/openapi.json",
        status=404,
    )
    with pytest.raises(HTTPError):
        get_openapi_schema("http://localhost")


@responses.activate
def test_call_api():
    """Calling the API sould make a request with the given method."""
    body = {"test": True}
    responses.add(
        responses.GET,
        "http://localhost/test",
        json=body,
        status=200,
    )
    result = call_api("GET", "/test", {}, {}, "http://localhost")
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
        "http://localhost/openapi.json",
        json={},
    )
    with pytest.raises(SystemExit):
        main(["--help"], "http://localhost")

    captured = capsys.readouterr()
    assert "usage" in captured.out
