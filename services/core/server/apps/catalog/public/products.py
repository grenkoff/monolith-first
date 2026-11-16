"""Products of the catalog as other modules see them."""

from typing import final
from uuid import UUID

import msgspec


@final
class Product(msgspec.Struct, frozen=True):
    """Product on sale: its id, name and price in cents."""

    id: UUID
    name: str
    price_cents: int
