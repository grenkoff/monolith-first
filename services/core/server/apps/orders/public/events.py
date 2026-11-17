"""Facts that orders publish for other modules."""

from typing import Final, final
from uuid import UUID

import msgspec

ORDER_PLACED: Final = 'orders.v1.order_placed'


@final
class OrderPlaced(msgspec.Struct, frozen=True):
    """Fact that an order for a quantity of a product was placed."""

    id: UUID
    order: UUID
    product: UUID
    quantity: int
