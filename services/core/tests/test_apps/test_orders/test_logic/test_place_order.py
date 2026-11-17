"""Tests of the use case that places orders."""

from typing import final
from uuid import UUID, uuid7

import attrs

from server.apps.orders.logic.orders import UnknownOrderError
from server.apps.orders.logic.usecases.place_order import PlaceOrder
from server.apps.orders.logic.value_objects import Order, OrderDraft


@final
@attrs.define(slots=True, frozen=True)
class _ListedPrices:
    """Fake: prices of the products listed in a mapping."""

    _cents: dict[UUID, int]

    def price_cents(self, product: UUID) -> int:
        """Returns the listed price of the product."""
        return self._cents[product]


@final
@attrs.define(slots=True, frozen=True)
class _UnsavedOrders:
    """Fake: orders that get a fresh id and are kept nowhere."""

    def add(self, draft: OrderDraft, total_cents: int) -> Order:
        """Returns the order as if it was saved."""
        return Order(
            id=uuid7(),
            product=draft.product,
            quantity=draft.quantity,
            total_cents=total_cents,
        )

    def order(self, identifier: UUID) -> Order:
        """Finds nothing, since nothing is kept."""
        raise UnknownOrderError(str(identifier))


def test_order_total_comes_from_catalog_price() -> None:
    product = uuid7()

    order = PlaceOrder(_ListedPrices({product: 350}), _UnsavedOrders())(
        OrderDraft(product=product, quantity=3),
    )

    assert order.total_cents == 1050
