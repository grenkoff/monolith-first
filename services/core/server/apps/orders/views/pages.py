"""Pages of orders rendered on the server."""

from typing import final
from uuid import UUID

from django.http import HttpRequest, HttpResponse
from django.views import View

from server.common.di import HasContainer


@final
class PlaceOrderForm(HasContainer, View):
    """Order form posted from a product page."""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Places the order from the form and shows it."""
        return HttpResponse(request.path)


@final
class OrderPage(HasContainer, View):
    """Page of a placed order."""

    def get(self, request: HttpRequest, identifier: UUID) -> HttpResponse:
        """Renders the order with the id from the path."""
        return HttpResponse(str(identifier))
