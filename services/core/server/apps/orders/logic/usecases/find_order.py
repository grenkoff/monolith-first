"""Use case that finds a placed order."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import attrs

if TYPE_CHECKING:
    from uuid import UUID

    from server.apps.orders.logic.orders import Orders
    from server.apps.orders.logic.value_objects import Order


@final
@attrs.define(slots=True, frozen=True)
class FindOrder:
    """Finds placed orders by id."""

    _orders: Orders

    def __call__(self, identifier: UUID) -> Order:
        """Returns the order with the id."""
        return self._orders.order(identifier)
