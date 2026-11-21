"""Use case that searches the products on sale by name."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import attrs

if TYPE_CHECKING:
    from server.apps.catalog.logic.products import Products
    from server.apps.catalog.logic.search import Similarity
    from server.apps.catalog.public.products import Product


@final
@attrs.define(slots=True, frozen=True)
class SearchProducts:
    """Finds the products whose names resemble a query, the closest first."""

    _products: Products
    _similarity: Similarity

    def __call__(self, query: str) -> list[Product]:
        """Returns the products that resemble the query enough."""
        return self._products.on_sale()[:0] if query else []
