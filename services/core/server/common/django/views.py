"""Pages of the site that belong to no module."""

from typing import Any, final, override

from django.conf import settings
from django.views.generic import TemplateView


@final
class DesignSystem(TemplateView):
    """Page that shows every component of the design system in every theme."""

    template_name = 'design/index.html'

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Adds the themes to show to the context of the page."""
        context = super().get_context_data(**kwargs)
        context['themes'] = settings.SITE_THEMES
        return context
