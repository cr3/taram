"""Memcached functions."""

from attrs import define
from pylibmc import Client


@define(frozen=True)
class Memcached:

    client: Client

    @classmethod
    def from_default(cls) -> "Memcached":
        """Instantiate a Memcached instance from default server."""
        return cls.from_server("memcached:11211")

    @classmethod
    def from_server(cls, server: str) -> "Memcached":
        """Instantiate a Memcached instance from a single server."""
        return cls.from_servers([server])

    @classmethod
    def from_servers(cls, servers: list[str]) -> "Memcached":
        """Instantiate a Memcached instance from a list of servers."""
        client = Client(
            servers,
            binary=True,
            behaviors={
                "tcp_nodelay": True,
                "ketama": True,
            },
        )
        return cls(client)

    def flush(self) -> bool:
        return self.client.flush_all()
