"""Products kept in the database of the catalog."""

from typing import TypedDict, final
from uuid import UUID

import attrs
from django.db.models import QuerySet, Sum
from django.db.models.functions import Coalesce
from django_stubs_ext import WithAnnotations

from server.apps.catalog import models
from server.apps.catalog.logic.value_objects import ProductDraft
from server.apps.catalog.public.products import Product, UnknownProductError


@final
class _Sales(TypedDict):
    """Annotation of a stored product with the quantity it sold."""

    sold: int


type _Sold = WithAnnotations[models.Product, _Sales]


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
            stored = self._with_sales().get(pk=identifier)
        except models.Product.DoesNotExist as exc:
            raise UnknownProductError(str(identifier)) from exc
        return self._transferred(stored, stored.sold)

    def on_sale(self) -> list[Product]:
        """Reads every product with its sales, sorted by name."""
        return [
            self._transferred(stored, stored.sold)
            for stored in self._with_sales().order_by('name')
        ]

    def _with_sales(self) -> QuerySet[_Sold]:
        """Returns the products annotated with the quantity they sold."""
        return models.Product.objects.annotate(
            sold=Coalesce(Sum('sales__quantity'), 0),
        )

    def _transferred(self, stored: models.Product, sold: int) -> Product:
        """Turns a stored product into the transfer object of the catalog."""
        return Product(
            id=stored.id,
            name=stored.name,
            price_cents=stored.price_cents,
            sold=sold,
        )
