"""Value objects of orders."""

from typing import final
from uuid import UUID

import msgspec


@final
class OrderDraft(msgspec.Struct, frozen=True):
    """Order to place: a product and how many of it."""

    product: UUID
    quantity: int


@final
class Order(msgspec.Struct, frozen=True):
    """Order that was placed, with its id, product, quantity and total in cents."""

    id: UUID
    product: UUID
    quantity: int
    total_cents: int
