"""Queue abstraction and implementation."""

import os
from abc import ABC, abstractmethod
from collections import defaultdict
from contextlib import contextmanager, suppress
from time import time

from attrs import define, field
from redis import StrictRedis
from yarl import URL

from taram.registry import registry_load


class QueueEmpty(Exception):
    """Raised when the queue is empty."""


@define
class Queue(ABC):
    """Base queue class."""

    @classmethod
    def from_url(cls, url: URL | str, registry=None) -> "Queue":
        if registry is None:
            registry = registry_load("taram_queue")
        scheme = URL(url).scheme
        queue_cls = registry["taram_queue"][scheme]
        return queue_cls.from_url(url)

    @abstractmethod
    def subscribe(self, topic: str) -> None:
        """Subscribe to a topic before receiving messages."""

    @abstractmethod
    def unsubscribe(self, topic: str) -> None:
        """Unsubscribe from a topic after receiving messages."""

    @abstractmethod
    def receive(self, timeout=None) -> str:
        """Listen for messages on the subscribed topics."""

    @abstractmethod
    def publish(self, topic: str, message: str) -> None:
        """Publish a message to a topic."""

    @contextmanager
    def connect(self, topic: str) -> "Queue":
        """Context manager that subscribes on entry and unsubscribes on exit."""
        self.subscribe(topic)
        try:
            yield self
        finally:
            self.unsubscribe(topic)


_global_memory_queues = defaultdict(list)


@define
class MemoryQueue(Queue):

    topics = field(factory=list)
    queues = field(default=_global_memory_queues)

    @classmethod
    def from_url(cls, url: URL) -> "MemoryQueue":
        return cls()

    def subscribe(self, topic: str) -> None:
        """See `Queue.subscribe`."""
        self.topics.append(topic)

    def unsubscribe(self, topic: str) -> None:
        """See `Queue.unsubscribe`."""
        with suppress(ValueError):
            self.topics.remove(topic)

    def receive(self, timeout=None) -> str:
        """See `Queue.receive`."""
        for topic in self.topics[:]:
            # Cycle through topics.
            self.topics.append(self.topics.pop(0))
            queue = self.queues[topic]
            with suppress(IndexError):
                return queue.pop(0)

        raise QueueEmpty("Queue is empty")

    def publish(self, topic: str, message: str) -> None:
        """See `Queue.publish`."""
        queue = self.queues[topic]
        queue.append(message)


@define
class RedisQueue(Queue):

    client = field()
    pubsub = field()

    @classmethod
    def from_env(cls, env=os.environ) -> "RedisQueue":
        host = env.get("REDIS_SLAVEOF_IP", "") or env.get("IPV4_NETWORK", "172.22.1") + ".249"
        port = int(env.get("REDIS_SLAVEOF_PORT", "") or "6379")
        password = env.get("REDISPASS")
        return cls.from_host(host, port, password=password)

    @classmethod
    def from_host(cls, host: str, port: int = 6379, password: str | None = None) -> "RedisQueue":
        client = StrictRedis(
            host=host,
            port=port,
            decode_responses=True,
            db=0,
            password=password,
        )
        pubsub = client.pubsub(ignore_subscribe_messages=True)
        return cls(client, pubsub)

    @classmethod
    def from_url(cls, url: URL | str) -> "RedisQueue":
        url = URL(url)
        return cls.from_host(url.host, url.port, password=url.password)

    def subscribe(self, topic: str) -> None:
        """See `Queue.subscribe`."""
        self.pubsub.subscribe(topic)

    def unsubscribe(self, topic: str) -> None:
        """See `Queue.unsubscribe`."""
        self.pubsub.unsubscribe(topic)

    def receive(self, timeout=0) -> str:
        """See `Queue.receive`."""
        stop_time = time() + timeout
        while True:
            remaining_timeout = max(0, stop_time - time())
            if message := self.pubsub.get_message(timeout=remaining_timeout):
                return message["data"]
            if time() >= stop_time:
                raise QueueEmpty("Queue is empty")

    def publish(self, topic: str, message: str) -> None:
        """See `Queue.publish`."""
        self.client.publish(topic, message)
