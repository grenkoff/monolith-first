"""Relay of the outbox with the subscribers of every topic."""

import punq

from server.apps.catalog.infra import sales
from server.apps.orders.public import events
from server.common.outbox.relay import Relay


def inject(container: punq.Container) -> None:
    """Registers the relay with the subscribers of every topic."""
    container.register(
        Relay,
        instance=Relay({events.ORDER_PLACED: (sales.RecordedSales(),)}),
    )
