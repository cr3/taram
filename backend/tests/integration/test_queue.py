"""Integration tests for the queue module."""

import pytest

from taram.queue import QueueEmpty


def test_queue_send_receive(queue, unique):
    """Sending a message to a queue should be the next received message."""
    topic = unique("text")
    with queue.connect(topic) as session:
        session.publish(topic, "test")
        result = session.receive(5)
    assert result == "test"


def test_queue_receive_empty(queue, unique):
    """Receiving from an empty queue should raise a QueueEmpty error."""
    topic = unique("text")
    with queue.connect(topic) as session, pytest.raises(QueueEmpty):
        session.receive()
