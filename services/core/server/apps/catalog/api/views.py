"""HTTP controllers of the catalog API."""

from http import HTTPStatus
from typing import final, override

from django.http import HttpResponse
from dmr import Body, Controller, modify
from dmr.endpoint import Endpoint
from dmr.errors import ErrorType
from dmr.metadata import ResponseSpec

from server.apps.catalog.logic.usecases import add_product, find_product
from server.apps.catalog.logic.value_objects import ProductDraft
from server.apps.catalog.public.products import Product, UnknownProductError
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


@final
class ProductGet(
    HasContainer,
    Controller[StrictMsgspecSerializer],
):
    """Shows products on sale over HTTP."""

    @modify(
        extra_responses=[
            ResponseSpec(
                Controller.error_model,
                status_code=HTTPStatus.NOT_FOUND,
            ),
        ],
    )
    def get(self) -> Product:
        """Returns the product with the id from the path."""
        return self.resolve(find_product.FindProduct)(self.kwargs['id'])

    @override
    def handle_error(
        self,
        endpoint: Endpoint,
        controller: Controller[StrictMsgspecSerializer],
        exc: Exception,
    ) -> HttpResponse:
        """Answers 404 when the catalog has no such product."""
        if isinstance(exc, UnknownProductError):
            return self.to_error(
                self.format_error(
                    'Product not found',
                    error_type=ErrorType.not_found,
                ),
                status_code=HTTPStatus.NOT_FOUND,
            )
        return super().handle_error(endpoint, controller, exc)
