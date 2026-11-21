"""Routes of the catalog HTTP API."""

from dmr.routing import Router, path

from server.apps.catalog.api import photos, views

router = Router(
    'catalog/',
    [
        path('products/', views.ProductCreate.as_view(), name='product_create'),
        path(
            'products/<uuid:id>/',
            views.ProductGet.as_view(),
            name='product_get',
        ),
        path(
            'products/<uuid:id>/photo/',
            photos.ProductPhoto.as_view(),
            name='product_photo',
        ),
    ],
)
