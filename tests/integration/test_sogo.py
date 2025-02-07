"""Integration tests for the SOGo service."""

import requests
from hamcrest import (
    assert_that,
    contains_string,
)


def test_sogo(sogo_client, unique):
    """The SOGo service should... ."""
    response = requests.get(f"http://{sogo_client.ip}:20000/SOGo.index/", timeout=10)
    assert_that(response.text, contains_string("SOGo Groupware"))
