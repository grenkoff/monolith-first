"""HTTP controllers of the orders API."""

from typing import final
from uuid import UUID

from dmr import Body, Controller

from server.apps.orders.logic.value_objects import Order, OrderDraft
from server.common.serializers import StrictMsgspecSerializer


@final
class OrderCreate(Controller[StrictMsgspecSerializer]):
    """Places orders over HTTP."""

    def post(self, parsed_body: Body[OrderDraft]) -> Order:
        """Places the order from the request body."""
        return Order(
            id=UUID(int=0),
            product=parsed_body.product,
            quantity=parsed_body.quantity,
            total_cents=0,
        )
