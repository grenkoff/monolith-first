"""Values that every template of the site reads."""

from django.conf import settings
from django.http import HttpRequest


def site(_request: HttpRequest) -> dict[str, object]:
    """Returns the name, the theme and the themes to switch to for the layout."""
    return {
        'site_name': settings.SITE_NAME,
        'theme': settings.SITE_THEME,
        'themes': settings.SITE_THEMES,
        'theme_switcher': settings.SITE_THEME_SWITCHER,
    }
