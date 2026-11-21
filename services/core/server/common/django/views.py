"""Pages of the site that belong to no module."""

from typing import final

from django.http import HttpRequest, HttpResponse
from django.views import View


@final
class DesignSystem(View):
    """Page that shows every component of the design system in every theme."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Renders the components in each theme."""
        return HttpResponse(request.path)
