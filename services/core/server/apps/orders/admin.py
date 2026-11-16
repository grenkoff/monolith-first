"""Admin panel of orders."""

from django.contrib import admin

from server.apps.orders.models import Order

admin.site.register(Order)
