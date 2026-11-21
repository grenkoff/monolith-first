"""Routes of the pages of the catalog."""

from django.urls import path

from server.apps.catalog.views import pages

urlpatterns = [
    path('', pages.Home.as_view(), name='home'),
    path(
        'products/<uuid:identifier>/',
        pages.ProductPage.as_view(),
        name='product',
    ),
]
