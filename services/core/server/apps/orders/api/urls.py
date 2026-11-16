"""Routes of the orders HTTP API."""

from dmr.routing import Router, path

from server.apps.orders.api import views

router = Router(
    'orders/',
    [
        path('', views.OrderCreate.as_view(), name='order_create'),
    ],
)
