"""Admin panel of the catalog."""

from django.contrib import admin

from server.apps.catalog.models import Product

admin.site.register(Product)
