"""HTTP controllers of the orders API."""

from http import HTTPStatus
from typing import final, override

from django.http import HttpResponse
from dmr import Body, Controller, modify
from dmr.endpoint import Endpoint
from dmr.errors import ErrorType
from dmr.metadata import ResponseSpec

from server.apps.orders.logic.orders import (
    ProductNotOnSaleError,
    UnknownOrderError,
)
from server.apps.orders.logic.usecases import find_order, place_order
from server.apps.orders.logic.value_objects import Order, OrderDraft
from server.common.di import HasContainer
from server.common.serializers import StrictMsgspecSerializer


@final
class OrderCreate(
    HasContainer,
    Controller[StrictMsgspecSerializer],
):
    """Places orders over HTTP."""

    @modify(
        extra_responses=[
            ResponseSpec(
                Controller.error_model,
                status_code=HTTPStatus.CONFLICT,
            ),
        ],
    )
    def post(self, parsed_body: Body[OrderDraft]) -> Order:
        """Places the order from the request body."""
        return self.resolve(place_order.PlaceOrder)(parsed_body)

    @override
    def handle_error(
        self,
        endpoint: Endpoint,
        controller: Controller[StrictMsgspecSerializer],
        exc: Exception,
    ) -> HttpResponse:
        """Answers 409 when the ordered product is not on sale."""
        if isinstance(exc, ProductNotOnSaleError):
            return self.to_error(
                self.format_error(
                    'Product is not on sale',
                    error_type=ErrorType.user_msg,
                ),
                status_code=HTTPStatus.CONFLICT,
            )
        return super().handle_error(endpoint, controller, exc)


@final
class OrderGet(
    HasContainer,
    Controller[StrictMsgspecSerializer],
):
    """Shows placed orders over HTTP."""

    @modify(
        extra_responses=[
            ResponseSpec(
                Controller.error_model,
                status_code=HTTPStatus.NOT_FOUND,
            ),
        ],
    )
    def get(self) -> Order:
        """Returns the order with the id from the path."""
        return self.resolve(find_order.FindOrder)(self.kwargs['id'])

    @override
    def handle_error(
        self,
        endpoint: Endpoint,
        controller: Controller[StrictMsgspecSerializer],
        exc: Exception,
    ) -> HttpResponse:
        """Answers 404 when no order has the id."""
        if isinstance(exc, UnknownOrderError):
            return self.to_error(
                self.format_error(
                    'Order not found',
                    error_type=ErrorType.not_found,
                ),
                status_code=HTTPStatus.NOT_FOUND,
            )
        return super().handle_error(endpoint, controller, exc)
