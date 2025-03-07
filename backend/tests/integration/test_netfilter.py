"""Integration tests for the netfilter service."""

from unittest.mock import Mock

from taram.netfilter import (
    NetfilterService,
)


def test_netfilter_service_watch(redis_client):
    """Watching should ban when a message matches on the F2B_CHANNEL."""
    netfilter = Mock()
    pubsub = redis_client.pubsub()
    pubsub.subscribe("F2B_CHANNEL")
    service = NetfilterService(netfilter, pubsub)

    def ban(_):
        service.exit_now = True

    netfilter.ban.side_effect = ban
    redis_client.publish(
        "F2B_CHANNEL",
        "mail UI: Invalid password for .+ by 1.2.3.4",
    )

    service.watch()

    netfilter.ban.assert_called_once()
