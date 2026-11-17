"""Objects of orders, built for the composition root."""

import punq

from server.apps.catalog.public.products import Catalog
from server.apps.orders.infra import catalog, orders
from server.apps.orders.logic.usecases import find_order, place_order
from server.common.outbox.outbox import StoredOutbox


def inject(container: punq.Container, facade: Catalog) -> None:
    """Registers the objects of orders, with the catalog behind its facade."""
    stored = orders.StoredOrders(StoredOutbox())
    container.register(
        place_order.PlaceOrder,
        instance=place_order.PlaceOrder(catalog.CatalogPrices(facade), stored),
    )
    container.register(
        find_order.FindOrder,
        instance=find_order.FindOrder(stored),
    )
