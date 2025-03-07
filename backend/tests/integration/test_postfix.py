"""Integration tests for the Postfix service."""

import socket


def get_postfix_banner(server, port=589):
    """Get the banner from Postfix."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((server, port))
        banner = s.recv(1024).decode("utf-8")
        return banner.strip()


def test_postfix_service(postfix_service):
    """The Postfix service should return a banner."""
    banner = get_postfix_banner(postfix_service.ip)
    assert "ESMTP Postfix" in banner
