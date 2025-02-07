"""Integration tests for the Dovecot service."""

import socket


def _test_dovecot_auth(dovecot_client):
    """The Dovecot auth service should return the VERSION on port 10001."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((dovecot_client.ip, 10001))
        result = s.recv(7)
        assert result == b"VERSION"
