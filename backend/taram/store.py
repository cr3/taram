"""Key/value store abstraction layer."""

import os
from abc import ABCMeta, abstractmethod
from contextlib import suppress
from functools import wraps

from attrs import define, field
from redis import StrictRedis
from redis.exceptions import ResponseError
from yarl import URL

from taram.registry import registry_load


class Store(metaclass=ABCMeta):

    @classmethod
    def from_env(cls, env=os.environ, registry=None) -> "Store":
        if "REDISPASS" in env:
            host = env.get("REDIS_SLAVEOF_IP", "") or env.get("IPV4_NETWORK", "172.22.1") + ".249"
            port = int(env.get("REDIS_SLAVEOF_PORT", "") or "6379")
            password = env.get("REDISPASS")
            url = URL.build(scheme="redis", password=password, host=host, port=port)
        else:
            url = URL.build(scheme="memory")

        return cls.from_url(url)

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


@define(frozen=True)
class MemoryStore(Store):
    """Memory implementation of a store."""

    data: dict[str, str | dict[str, str]] = field(factory=dict)

    @classmethod
    def from_url(cls, url: URL | str) -> "MemoryStore":
        return cls()

    def get(self, key: str) -> str:
        """See `Store.get`."""
        value = self.data.get(key)
        if value is not None and not isinstance(value, str):
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
        data = self.data.get(key, {})
        for f in fields:
            with suppress(KeyError):
                del data[f]
                count += 1

        return count


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
    def from_url(cls, url: URL | str) -> "RedisStore":
        url = URL(url)
        return cls(host=url.host, port=url.port, decode_responses=True, db=0, password=url.password)

    get = wrap_response_error(StrictRedis.get)
    hget = wrap_response_error(StrictRedis.hget)
    hgetall = wrap_response_error(StrictRedis.hgetall)
    hset = wrap_response_error(StrictRedis.hset)
