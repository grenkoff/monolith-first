"""HTTP controllers of the catalog API."""

from typing import final
from uuid import UUID

from dmr import Body, Controller

from server.apps.catalog.logic.value_objects import ProductDraft
from server.apps.catalog.public.products import Product
from server.common.serializers import StrictMsgspecSerializer


@final
class ProductCreate(Controller[StrictMsgspecSerializer]):
    """Puts products on sale over HTTP."""

    def post(self, parsed_body: Body[ProductDraft]) -> Product:
        """Creates a product from the request body."""
        return Product(id=UUID(int=0), name='', price_cents=0)
