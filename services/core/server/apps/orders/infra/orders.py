"""Orders kept in the database of the orders module."""

from typing import final
from uuid import UUID, uuid7

import attrs
from django.db import transaction

from server.apps.orders import models
from server.apps.orders.logic.orders import UnknownOrderError
from server.apps.orders.logic.value_objects import Order, OrderDraft
from server.apps.orders.public.events import ORDER_PLACED, OrderPlaced
from server.common.outbox.outbox import Outbox


@final
@attrs.define(slots=True, frozen=True)
class StoredOrders:
    """Orders kept in the tables of the orders module."""

    _outbox: Outbox

    def add(self, draft: OrderDraft, total_cents: int) -> Order:
        """Saves a new order and its placed event in one transaction."""
        with transaction.atomic():
            stored = models.Order.objects.create(
                product=draft.product,
                quantity=draft.quantity,
                total_cents=total_cents,
            )
            self._outbox.add(
                ORDER_PLACED,
                OrderPlaced(
                    id=uuid7(),
                    order=stored.id,
                    product=stored.product,
                    quantity=stored.quantity,
                ),
            )
        return self._transferred(stored)

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
