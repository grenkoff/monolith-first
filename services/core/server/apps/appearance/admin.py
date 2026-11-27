"""Admin panel of appearance."""

from django.contrib import admin

from server.apps.appearance.models import ThemeChoice

admin.site.register(ThemeChoice)
