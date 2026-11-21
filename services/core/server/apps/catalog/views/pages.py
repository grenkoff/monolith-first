"""Pages of the catalog rendered on the server."""

from typing import final
from uuid import UUID

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from server.apps.catalog.logic.usecases import (
    find_product,
    list_products,
    search_products,
)
from server.apps.catalog.public.products import UnknownProductError
from server.common.di import HasContainer
from server.common.money import Cents


@final
class Home(HasContainer, View):
    """Home page that lists the products on sale."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Renders the products on sale with their prices."""
        products = self.resolve(list_products.ListProducts)()
        return render(
            request,
            'catalog/home.html',
            {
                'products': [
                    (product, Cents(product.price_cents)) for product in products
                ],
            },
        )


@final
class ProductPage(HasContainer, View):
    """Page of one product with a form to order it."""

    def get(self, request: HttpRequest, identifier: UUID) -> HttpResponse:
        """Renders the product with the id from the path, or answers 404."""
        try:
            product = self.resolve(find_product.FindProduct)(identifier)
        except UnknownProductError as exc:
            raise Http404(str(identifier)) from exc
        return render(
            request,
            'catalog/product.html',
            {'product': product, 'price': Cents(product.price_cents)},
        )


@final
class Search(HasContainer, View):
    """Page that finds products by a name typed with mistakes."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Renders the form and the products that resemble the query."""
        query = request.GET.get('q', '')
        products = self.resolve(search_products.SearchProducts)(query)
        return render(
            request,
            'catalog/search.html',
            {
                'query': query,
                'products': [
                    (product, Cents(product.price_cents)) for product in products
                ],
            },
        )


@final
class ProductThumbnail(HasContainer, View):
    """Thumbnail of the photo of a product, as a JPEG."""

    def get(self, request: HttpRequest, identifier: UUID) -> HttpResponse:
        """Answers the thumbnail of the product in the path, or 404."""
        return HttpResponse(request.path + str(identifier))
