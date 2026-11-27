"""Values of appearance that every template of the site reads."""

from typing import final

from django.conf import settings
from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject

from server.apps.appearance.logic.usecases.current_theme import CurrentTheme
from server.common.di import HasContainer


@final
class _Layout(HasContainer):
    """Resolves the use cases of appearance for the layout."""


def _current() -> str:
    """Returns the theme of the site from its use case."""
    return _Layout().resolve(CurrentTheme)()


def theme_context(_request: HttpRequest) -> dict[str, object]:
    """Returns the theme, read once a template needs it, and the themes."""
    return {
        'theme': SimpleLazyObject(_current),
        'themes': settings.SITE_THEMES,
    }
