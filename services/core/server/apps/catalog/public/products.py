"""Products of the catalog as other modules see them."""

from typing import Protocol, final
from uuid import UUID

import msgspec


@final
class Product(msgspec.Struct, frozen=True):
    """Product on sale: its id, name and price in cents."""

    id: UUID
    name: str
    price_cents: int


@final
class UnknownProductError(LookupError):
    """Raised when the catalog has no product with the given id."""

    __slots__ = ()


class Catalog(Protocol):
    """Facade: products of the catalog, as other modules ask for them."""

    def product(self, identifier: UUID) -> Product:
        """Returns the product with the id or raises UnknownProductError."""
