"""Use case that finds a product on sale."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import attrs

if TYPE_CHECKING:
    from uuid import UUID

    from server.apps.catalog.public.products import Catalog, Product


@final
@attrs.define(slots=True, frozen=True)
class FindProduct:
    """Finds products on sale in the catalog by id."""

    _catalog: Catalog

    def __call__(self, identifier: UUID) -> Product:
        """Returns the product with the id."""
        return self._catalog.product(identifier)
