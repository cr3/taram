"""Unit tests for the db module."""

import pytest

from taram.db import get_url


@pytest.mark.parametrize(
    "env, expected",
    [
        ({"DBDRIVER": "driver"}, "driver://"),
        ({"DBDRIVER": "driver", "DBUSER": "user"}, "driver://user@"),
        ({"DBDRIVER": "driver", "DBUSER": "user", "DBPASS": "pass"}, "driver://user:pass@"),
        ({"DBDRIVER": "driver", "DBPORT": "1234"}, "driver://:1234"),
        ({"DBDRIVER": "driver", "DBNAME": "name"}, "driver:///name"),
    ],
)
def test_get_url(env, expected):
    """Getting a URL should get DB variables from the environment."""
    url = get_url(env)
    assert url.render_as_string(hide_password=False) == expected
