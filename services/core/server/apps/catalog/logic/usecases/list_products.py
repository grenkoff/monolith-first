"""Use case that lists the products on sale."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import attrs

if TYPE_CHECKING:
    from server.apps.catalog.logic.products import Products
    from server.apps.catalog.public.products import Product


@final
@attrs.define(slots=True, frozen=True)
class ListProducts:
    """Lists every product on sale, sorted by name."""

    _products: Products

    def __call__(self) -> list[Product]:
        """Returns the products on sale."""
        return self._products.on_sale()
