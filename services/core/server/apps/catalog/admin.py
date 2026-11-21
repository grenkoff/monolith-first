"""Admin panel of the catalog."""

from django.contrib import admin

from server.apps.catalog.models import Photo, Product, Sale

admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(Photo)
