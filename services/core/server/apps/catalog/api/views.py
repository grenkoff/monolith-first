"""HTTP controllers of the catalog API."""

from typing import final

from dmr import Body, Controller

from server.apps.catalog.logic.usecases import add_product
from server.apps.catalog.logic.value_objects import ProductDraft
from server.apps.catalog.public.products import Product
from server.common.di import HasContainer
from server.common.serializers import StrictMsgspecSerializer


@final
class ProductCreate(
    HasContainer,
    Controller[StrictMsgspecSerializer],
):
    """Puts products on sale over HTTP."""

    def post(self, parsed_body: Body[ProductDraft]) -> Product:
        """Creates a product from the request body."""
        return self.resolve(add_product.AddProduct)(parsed_body)
