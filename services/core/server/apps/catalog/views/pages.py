"""Pages of the catalog rendered on the server."""

from typing import final
from uuid import UUID

from django.http import HttpRequest, HttpResponse
from django.views import View

from server.common.di import HasContainer


@final
class Home(HasContainer, View):
    """Home page: the products on sale."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Renders the products on sale."""
        return HttpResponse(request.path)


@final
class ProductPage(HasContainer, View):
    """Page of one product with a form to order it."""

    def get(self, request: HttpRequest, identifier: UUID) -> HttpResponse:
        """Renders the product with the id from the path."""
        return HttpResponse(str(identifier))
