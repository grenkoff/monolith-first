"""Use case that searches the products on sale by name."""

from __future__ import annotations

import operator
from typing import TYPE_CHECKING, final

import attrs

from server.apps.catalog.logic.constants import RESEMBLANCE_MIN

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
        if not query.strip():
            return []
        products = self._products.on_sale()
        scores = self._similarity.scores(
            query,
            [product.name for product in products],
        )
        ranked = sorted(
            zip(scores, products, strict=True),
            key=operator.itemgetter(0),
            reverse=True,
        )
        return [product for score, product in ranked if score >= RESEMBLANCE_MIN]
