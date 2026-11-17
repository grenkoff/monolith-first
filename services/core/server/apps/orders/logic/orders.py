"""Interfaces and errors of orders."""

from typing import Protocol, final
from uuid import UUID

from server.apps.orders.logic.value_objects import Order, OrderDraft


@final
class ProductNotOnSaleError(LookupError):
    """Raised when the ordered product is not on sale."""

    __slots__ = ()


@final
class UnknownOrderError(LookupError):
    """Raised when no order has the given id."""

    __slots__ = ()


class Prices(Protocol):
    """Current prices of the products that can be ordered."""

    def price_cents(self, product: UUID) -> int:
        """Returns the price in cents or raises ProductNotOnSaleError."""


class Orders(Protocol):
    """Placed orders, kept by the orders module."""

    def add(self, draft: OrderDraft, total_cents: int) -> Order:
        """Keeps the order with its total and returns it."""

    def order(self, identifier: UUID) -> Order:
        """Returns the order with the id or raises UnknownOrderError."""
