"""Value objects of the catalog."""

from typing import final

import msgspec


@final
class ProductDraft(msgspec.Struct, frozen=True):
    """Product to put on sale: a name and a price in cents."""

    name: str
    price_cents: int
