"""HTTP controllers of the orders API."""

from typing import final

from dmr import Body, Controller

from server.apps.orders.logic.usecases import place_order
from server.apps.orders.logic.value_objects import Order, OrderDraft
from server.common.di import HasContainer
from server.common.serializers import StrictMsgspecSerializer


@final
class OrderCreate(
    HasContainer,
    Controller[StrictMsgspecSerializer],
):
    """Places orders over HTTP."""

    def post(self, parsed_body: Body[OrderDraft]) -> Order:
        """Places the order from the request body."""
        return self.resolve(place_order.PlaceOrder)(parsed_body)
