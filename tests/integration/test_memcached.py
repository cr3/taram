"""Integration tests for the Memcached service."""

import socket


def test_memcached(memcached_client):
    """The Memcached service should allow connection from DBUSER."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((memcached_client.ip, 11211))
        s.send(b"stats\n")
        result = s.recv(8)
        assert result == b"STAT pid"
