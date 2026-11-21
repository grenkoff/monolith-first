"""Pages of the site that belong to no module."""

from typing import final

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View


@final
class DesignSystem(View):
    """Page that shows every component of the design system in every theme."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Renders the components once for each theme."""
        return render(
            request,
            'design/index.html',
            {'themes': settings.SITE_THEMES},
        )
