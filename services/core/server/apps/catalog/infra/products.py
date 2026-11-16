"""Products kept in the database of the catalog."""

from typing import final

import attrs

from server.apps.catalog import models
from server.apps.catalog.logic.value_objects import ProductDraft
from server.apps.catalog.public.products import Product


@final
@attrs.define(slots=True, frozen=True)
class StoredProducts:
    """Products kept in the tables of the catalog."""

    def add(self, draft: ProductDraft) -> Product:
        """Saves a new product and returns it."""
        stored = models.Product.objects.create(
            name=draft.name,
            price_cents=draft.price_cents,
        )
        return Product(
            id=stored.id,
            name=stored.name,
            price_cents=stored.price_cents,
        )
