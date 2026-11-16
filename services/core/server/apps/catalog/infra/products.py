"""Products kept in the database of the catalog."""

from typing import final
from uuid import UUID

import attrs

from server.apps.catalog import models
from server.apps.catalog.logic.value_objects import ProductDraft
from server.apps.catalog.public.products import Product, UnknownProductError


@final
@attrs.define(slots=True, frozen=True)
class StoredProducts:
    """Products kept in the tables of the catalog."""

    def add(self, draft: ProductDraft) -> Product:
        """Saves a new product and returns it."""
        return self._transferred(
            models.Product.objects.create(
                name=draft.name,
                price_cents=draft.price_cents,
            ),
        )

    def product(self, identifier: UUID) -> Product:
        """Reads the product with the id or raises UnknownProductError."""
        try:
            stored = models.Product.objects.get(pk=identifier)
        except models.Product.DoesNotExist as exc:
            raise UnknownProductError(str(identifier)) from exc
        return self._transferred(stored)

    def _transferred(self, stored: models.Product) -> Product:
        """Turns a stored product into the transfer object of the catalog."""
        return Product(
            id=stored.id,
            name=stored.name,
            price_cents=stored.price_cents,
        )
