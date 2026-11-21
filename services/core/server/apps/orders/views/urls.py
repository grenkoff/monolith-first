"""Routes of the pages of orders."""

from django.urls import path

from server.apps.orders.views import pages

app_name = 'orders'

urlpatterns = [
    path('orders/', pages.PlaceOrderForm.as_view(), name='place'),
    path(
        'orders/<uuid:identifier>/',
        pages.OrderPage.as_view(),
        name='order',
    ),
]
