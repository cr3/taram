"""Integration tests for the unbound service."""

from dns.nameserver import Do53Nameserver
from dns.resolver import LifetimeTimeout, Resolver
from pytest_xdocker.retry import retry


def resolve(name, ip, port=53):
    """Resolve for address records."""
    nameserver = Do53Nameserver(ip, port)
    resolver = Resolver()
    resolver.nameservers = [nameserver]
    return resolver.resolve_name(name, lifetime=60)


def test_unbound_resolve(unbound_service):
    """The unbound service should resolve domain names."""
    answer = retry(resolve, "github.com", unbound_service.ip).catching(LifetimeTimeout)
    assert answer.canonical_name().to_text() == "github.com."
