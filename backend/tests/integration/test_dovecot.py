"""Integration tests for the Dovecot service."""

import socket


def test_dovecot_auth(dovecot_service):
    """The Dovecot auth service should return the VERSION on port 10001."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((dovecot_service.ip, 10001))
        result = s.recv(7)
        assert result == b"VERSION"
