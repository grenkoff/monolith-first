"""Interfaces of the catalog."""

from typing import Protocol

from server.apps.catalog.logic.value_objects import ProductDraft
from server.apps.catalog.public.products import Product


class Products(Protocol):
    """Products on sale, kept by the catalog."""

    def add(self, draft: ProductDraft) -> Product:
        """Puts a product on sale and returns it."""
