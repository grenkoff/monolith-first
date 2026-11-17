"""Value objects of orders."""

from typing import Annotated, final
from uuid import UUID

import msgspec

from server.apps.orders.logic.constants import QUANTITY_MAX


@final
class OrderDraft(msgspec.Struct, frozen=True):
    """Order to place: a product and how many of it."""

    product: UUID
    quantity: Annotated[int, msgspec.Meta(ge=1, le=QUANTITY_MAX)]


@final
class Order(msgspec.Struct, frozen=True):
    """Order that was placed, with its id, product, quantity and total in cents."""

    id: UUID
    product: UUID
    quantity: int
    total_cents: int
