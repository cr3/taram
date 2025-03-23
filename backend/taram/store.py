"""Key/value store abstraction layer."""

import json
import os
from abc import ABC, abstractmethod
from contextlib import suppress
from functools import wraps

from attrs import define, field
from pylibmc import Client
from redis import StrictRedis
from redis.exceptions import ResponseError
from yarl import URL

from taram.registry import registry_load


@define
class Store(ABC):

    @classmethod
    def from_url(cls, url: URL | str, registry=None) -> "Store":
        if registry is None:
            registry = registry_load("taram_store")
        scheme = URL(url).scheme
        storage_cls = registry["taram_store"][scheme]
        return storage_cls.from_url(url)

    @abstractmethod
    def get(self, key: str) -> str:
        """Get the value of key."""

    @abstractmethod
    def set(self, key: str, value: str) -> bool:  # noqa: A003
        """Set key to hold the string value."""

    @abstractmethod
    def delete(self, *keys: str) -> int:
        """Removes the specified keys."""

    @abstractmethod
    def hget(self, key: str, field: str) -> str:
        """Returns the value associated with field in the hash stored at key."""

    @abstractmethod
    def hgetall(self, key: str) -> str:
        """Returns all fields and values of the hash stored at key."""

    @abstractmethod
    def hset(self, key: str, field: str, value: str) -> int:
        """Sets the specified field to a value in the hash stored at key."""

    @abstractmethod
    def hdel(self, key: str, *fields):
        """Removes the specified fields from the hash stored at key."""

    @abstractmethod
    def flushall(self):
        """Delete all the keys of all the existing databases, not just the currently selected one."""


@define(frozen=True)
class MemcachedStore(Store):
    """Memcached implementation of a store."""

    client = field()

    @classmethod
    def from_host(cls, host: str, port: int = 11211) -> "MemcachedStore":
        server = f"{host}:{port}"
        return cls.from_server(server)

    @classmethod
    def from_server(cls, server: str) -> "MemcachedStore":
        return cls.from_servers([server])

    @classmethod
    def from_servers(cls, servers: list[str]) -> "MemcachedStore":
        client = Client(
            servers,
            binary=True,
            behaviors={
                "tcp_nodelay": True,
                "ketama": True,
            },
        )
        return cls(client)

    @classmethod
    def from_url(cls, url: URL | str) -> "MemcachedStore":
        return cls.from_host(url.host, url.port)

    def get(self, key: str) -> str:
        """See `Store.get`."""
        try:
            value = self.client[key]
        except KeyError:
            return None

        with suppress(ValueError):
            data = json.loads(value)
            if isinstance(data, dict):
                raise TypeError("Wrong type")

        return value

    def set(self, key: str, value: str) -> bool:  # noqa: A003
        """See `Store.set`."""
        self.client.set(key, str(value))
        return True

    def delete(self, *keys: str) -> int:
        """See `Store.delete`."""
        return sum(self.client.delete(key) for key in keys)

    def hget(self, key: str, field: str) -> str:
        """See `Store.hget`."""
        payload = self.client.get(key, "{}")
        try:
            data = json.loads(payload)
        except ValueError as e:
            raise TypeError(str(e)) from e

        return data.get(field)

    def hgetall(self, key: str) -> str:
        """See `Store.hgetall`."""
        payload = self.client.get(key, "{}")
        with suppress(ValueError):
            return json.loads(payload)

        raise TypeError("Wrong type")

    def hset(self, key: str, field: str, value: str) -> int:  # F402
        """See `Store.hset`."""
        payload = self.client.get(key, "{}")
        try:
            data = json.loads(payload)
        except ValueError as e:
            raise TypeError(str(e)) from e

        count = 0 if field in data else 1
        data[field] = str(value)
        self.set(key, json.dumps(data))
        return count

    def hdel(self, key, *fields):
        """See `Store.hdel`."""
        count = 0
        data = self.hgetall(key)
        for f in fields:
            with suppress(KeyError):
                del data[f]
                count += 1

        if count:
            self.set(key, json.dumps(data))

        return count

    def flushall(self):
        """See `Store.flushall`."""
        self.client.flush_all()


@define(frozen=True)
class MemoryStore(Store):
    """Memory implementation of a store."""

    data: dict[str, str | dict[str, str]] = field(factory=dict)

    @classmethod
    def from_url(cls, url: URL | str) -> "MemoryStore":
        return cls()

    def get(self, key: str) -> str:
        """See `Store.get`."""
        try:
            value = self.data[key]
        except KeyError:
            return None

        if isinstance(value, dict):
            raise TypeError("Wrong type")

        return value

    def set(self, key: str, value: str) -> bool:  # noqa: A003
        """See `Store.set`."""
        self.data[key] = str(value)
        return True

    def delete(self, *keys: str) -> int:
        """See `Store.delete`."""
        count = 0
        for key in keys:
            with suppress(KeyError):
                del self.data[key]
                count += 1

        return count

    def hget(self, key: str, field: str) -> str:
        """See `Store.hget`."""
        try:
            return self.data.get(key, {}).get(field)
        except AttributeError as e:
            raise TypeError(str(e)) from e

    def hgetall(self, key: str) -> str:
        """See `Store.hgetall`."""
        value = self.data.get(key, {})
        if not isinstance(value, dict):
            raise TypeError("Wrong type")

        return value

    def hset(self, key: str, field: str, value: str) -> int:  # F402
        """See `Store.hset`."""
        data = self.data.setdefault(key, {})
        count = 0 if field in data else 1
        data[field] = str(value)
        return count

    def hdel(self, key, *fields):
        """See `Store.hdel`."""
        count = 0
        data = self.hgetall(key)
        for f in fields:
            with suppress(KeyError):
                del data[f]
                count += 1

        return count

    def flushall(self):
        """See `Store.flushall`."""
        self.data.clear()


def wrap_response_error(func):
    """Wrap a Redis ResponseError as a TypeError."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ResponseError as e:
            if "WRONGTYPE" in str(e):
                raise TypeError(str(e)) from e
            else:
                raise

    return wrapper


class RedisStore(StrictRedis, Store):
    """Redis implementation of a store."""

    @classmethod
    def from_env(cls, env=os.environ) -> "RedisStore":
        host = env.get("REDIS_SLAVEOF_IP", "") or env.get("IPV4_NETWORK", "172.22.1") + ".249"
        port = int(env.get("REDIS_SLAVEOF_PORT", "") or "6379")
        password = env.get("REDISPASS")
        return cls.from_host(host, port, password=password)

    @classmethod
    def from_host(cls, host: str, port: int = 6379, password: str | None = None) -> "RedisStore":
        return cls(
            host=host,
            port=port,
            decode_responses=True,
            db=0,
            password=password,
        )

    @classmethod
    def from_url(cls, url: URL | str) -> "RedisStore":
        url = URL(url)
        return cls.from_host(url.host, url.port, password=url.password)

    get = wrap_response_error(StrictRedis.get)
    hget = wrap_response_error(StrictRedis.hget)
    hgetall = wrap_response_error(StrictRedis.hgetall)
    hset = wrap_response_error(StrictRedis.hset)
