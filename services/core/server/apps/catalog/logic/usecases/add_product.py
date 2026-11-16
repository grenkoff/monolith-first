"""Use case that puts a product on sale."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import attrs

if TYPE_CHECKING:
    from server.apps.catalog.logic.products import Products
    from server.apps.catalog.logic.value_objects import ProductDraft
    from server.apps.catalog.public.products import Product


@final
@attrs.define(slots=True, frozen=True)
class AddProduct:
    """Puts products on sale in the catalog."""

    _products: Products

    def __call__(self, draft: ProductDraft) -> Product:
        """Adds the drafted product and returns it."""
        return self._products.add(draft)
