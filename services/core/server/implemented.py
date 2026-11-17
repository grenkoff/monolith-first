"""Composition root: builds the use cases of every module with their parts."""

import punq

from server.composition import catalog, greetings, orders, outbox


def populate_dependencies(container: punq.Container) -> punq.Container:
    """Registers the objects of every module in the container."""
    greetings.inject(container)
    orders.inject(container, catalog.inject(container))
    outbox.inject(container)
    return container
