"""Interfaces of orders."""

from typing import Protocol
from uuid import UUID

from server.apps.orders.logic.value_objects import Order, OrderDraft


class Prices(Protocol):
    """Current prices of the products that can be ordered."""

    def price_cents(self, product: UUID) -> int:
        """Returns the price of one item of the product in cents."""


class Orders(Protocol):
    """Placed orders, kept by the orders module."""

    def add(self, draft: OrderDraft, total_cents: int) -> Order:
        """Keeps the order with its total and returns it."""
