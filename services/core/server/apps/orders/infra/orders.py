"""Orders kept in the database of the orders module."""

from typing import final
from uuid import UUID

import attrs

from server.apps.orders import models
from server.apps.orders.logic.orders import UnknownOrderError
from server.apps.orders.logic.value_objects import Order, OrderDraft


@final
@attrs.define(slots=True, frozen=True)
class StoredOrders:
    """Orders kept in the tables of the orders module."""

    def add(self, draft: OrderDraft, total_cents: int) -> Order:
        """Saves a new order with its total and returns it."""
        return self._transferred(
            models.Order.objects.create(
                product=draft.product,
                quantity=draft.quantity,
                total_cents=total_cents,
            ),
        )

    def order(self, identifier: UUID) -> Order:
        """Reads the order with the id or raises UnknownOrderError."""
        try:
            stored = models.Order.objects.get(pk=identifier)
        except models.Order.DoesNotExist as exc:
            raise UnknownOrderError(str(identifier)) from exc
        return self._transferred(stored)

    def _transferred(self, stored: models.Order) -> Order:
        """Turns a stored order into its value object."""
        return Order(
            id=stored.id,
            product=stored.product,
            quantity=stored.quantity,
            total_cents=stored.total_cents,
        )
