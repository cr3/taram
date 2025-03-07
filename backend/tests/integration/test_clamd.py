"""Integration tests for the clamd service."""

import socket


def test_clamd_service(clamd_service):
    """Sending PING to the clamd service should return PONG."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((clamd_service.ip, 3310))
        s.send(b"PING\n")
        result = s.recv(5)
        assert result == b"PONG\n"
