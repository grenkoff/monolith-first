"""Objects of appearance, built for the composition root."""

import punq
from django.conf import settings

from server.apps.appearance.infra.themes import StoredThemes
from server.apps.appearance.logic.usecases.choose_theme import ChooseTheme
from server.apps.appearance.logic.usecases.current_theme import CurrentTheme


def inject(container: punq.Container) -> None:
    """Registers the use cases of appearance."""
    stored = StoredThemes()
    container.register(
        ChooseTheme,
        instance=ChooseTheme(stored, settings.SITE_THEMES),
    )
    container.register(
        CurrentTheme,
        instance=CurrentTheme(stored, settings.SITE_THEME),
    )
