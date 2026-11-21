"""Pages of orders rendered on the server."""

from http import HTTPStatus
from typing import Final, final
from uuid import UUID

import msgspec
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from server.apps.orders.logic import constants, orders, value_objects
from server.apps.orders.logic.usecases import find_order, place_order
from server.common.di import HasContainer
from server.common.money import Cents

_REFUSED: Final = 'orders/refused.html'


@final
class PlaceOrderForm(HasContainer, View):
    """Order form posted from a product page."""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Places the order from the form and redirects to its page."""
        try:
            draft = msgspec.convert(
                {
                    'product': request.POST.get('product', ''),
                    'quantity': request.POST.get('quantity', ''),
                },
                value_objects.OrderDraft,
                strict=False,
            )
        except msgspec.ValidationError:
            return render(
                request,
                _REFUSED,
                {'reason': f'Order from 1 to {constants.QUANTITY_MAX} items.'},
                status=HTTPStatus.BAD_REQUEST,
            )
        try:
            order = self.resolve(place_order.PlaceOrder)(draft)
        except orders.ProductNotOnSaleError:
            return render(
                request,
                _REFUSED,
                {'reason': 'The product is not on sale.'},
                status=HTTPStatus.CONFLICT,
            )
        return redirect('orders:order', identifier=order.id)


@final
class OrderPage(HasContainer, View):
    """Page of a placed order."""

    def get(self, request: HttpRequest, identifier: UUID) -> HttpResponse:
        """Renders the order with the id from the path, or answers 404."""
        try:
            order = self.resolve(find_order.FindOrder)(identifier)
        except orders.UnknownOrderError as exc:
            raise Http404(str(identifier)) from exc
        return render(
            request,
            'orders/order.html',
            {'order': order, 'total': Cents(order.total_cents)},
        )
