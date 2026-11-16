"""Use case that places an order."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import attrs

if TYPE_CHECKING:
    from server.apps.orders.logic.orders import Orders, Prices
    from server.apps.orders.logic.value_objects import Order, OrderDraft


@final
@attrs.define(slots=True, frozen=True)
class PlaceOrder:
    """Places orders at the current prices of the products."""

    _prices: Prices
    _orders: Orders

    def __call__(self, draft: OrderDraft) -> Order:
        """Keeps the order with the total it costs now."""
        return self._orders.add(draft, 0)
