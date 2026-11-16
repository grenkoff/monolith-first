"""Orders kept in the database of the orders module."""

from typing import final

import attrs

from server.apps.orders import models
from server.apps.orders.logic.value_objects import Order, OrderDraft


@final
@attrs.define(slots=True, frozen=True)
class StoredOrders:
    """Orders kept in the tables of the orders module."""

    def add(self, draft: OrderDraft, total_cents: int) -> Order:
        """Saves a new order with its total and returns it."""
        stored = models.Order.objects.create(
            product=draft.product,
            quantity=draft.quantity,
            total_cents=total_cents,
        )
        return Order(
            id=stored.id,
            product=stored.product,
            quantity=stored.quantity,
            total_cents=stored.total_cents,
        )
