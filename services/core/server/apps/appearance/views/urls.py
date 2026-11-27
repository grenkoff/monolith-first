"""Routes of the pages of appearance."""

from django.urls import path

from server.apps.appearance.views import pages

urlpatterns = [
    path('appearance/theme/', pages.ThemeForm.as_view(), name='theme'),
]
