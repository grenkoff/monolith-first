"""Prices of products, asked from the catalog through its facade."""

from typing import final
from uuid import UUID

import attrs

from server.apps.catalog.public.products import Catalog


@final
@attrs.define(slots=True, frozen=True)
class CatalogPrices:
    """Adapter: current prices of products from the catalog facade."""

    _catalog: Catalog

    def price_cents(self, product: UUID) -> int:
        """Asks the catalog for the product and returns its price."""
        return self._catalog.product(product).price_cents
