"""Products kept in the database of the catalog."""

from typing import final
from uuid import UUID

import attrs
from django.db.models import Sum
from django.db.models.functions import Coalesce

from server.apps.catalog import models
from server.apps.catalog.logic.value_objects import ProductDraft
from server.apps.catalog.public.products import Product, UnknownProductError


@final
@attrs.define(slots=True, frozen=True)
class StoredProducts:
    """Products kept in the tables of the catalog."""

    def add(self, draft: ProductDraft) -> Product:
        """Saves a new product, which has sold nothing yet, and returns it."""
        stored = models.Product.objects.create(
            name=draft.name,
            price_cents=draft.price_cents,
        )
        return self._transferred(stored, 0)

    def product(self, identifier: UUID) -> Product:
        """Reads the product with its sales or raises UnknownProductError."""
        try:
            stored = models.Product.objects.annotate(
                sold=Coalesce(Sum('sales__quantity'), 0),
            ).get(pk=identifier)
        except models.Product.DoesNotExist as exc:
            raise UnknownProductError(str(identifier)) from exc
        return self._transferred(stored, stored.sold)

    def _transferred(self, stored: models.Product, sold: int) -> Product:
        """Turns a stored product into the transfer object of the catalog."""
        return Product(
            id=stored.id,
            name=stored.name,
            price_cents=stored.price_cents,
            sold=sold,
        )
