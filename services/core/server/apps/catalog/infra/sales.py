"""Sales the catalog learns from the orders placed for its products."""

from typing import final

import attrs
import msgspec

from server.apps.catalog import models
from server.apps.orders.public.events import OrderPlaced
from server.common.outbox.relay import Envelope


@final
@attrs.define(slots=True, frozen=True)
class RecordedSales:
    """Observer: records each placed order as a sale of its product."""

    def receive(self, envelope: Envelope) -> None:
        """Keeps the sale under its event id, once however often it comes."""
        placed = msgspec.convert(envelope.payload, OrderPlaced)
        models.Sale.objects.get_or_create(
            id=placed.id,
            defaults={'product_id': placed.product, 'quantity': placed.quantity},
        )
