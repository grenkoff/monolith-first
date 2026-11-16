"""Routes of the catalog HTTP API."""

from dmr.routing import Router, path

from server.apps.catalog.api import views

router = Router(
    'catalog/',
    [
        path('products/', views.ProductCreate.as_view(), name='product_create'),
    ],
)
