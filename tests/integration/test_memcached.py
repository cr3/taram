"""Integration tests for the Memcached service."""

import socket

from taram.memcached import Memcached


def test_memcached_service(memcached_client):
    """The Memcached service should allow connection from DBUSER."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((memcached_client.ip, 11211))
        s.send(b"stats\n")
        result = s.recv(8)
        assert result == b"STAT pid"


def test_memcached_flush(memcached_client):
    """Flushing the Memcached service should return True."""
    memcached = Memcached.from_servers([f"{memcached_client.ip}:11211"])
    result = memcached.flush()
    assert result
