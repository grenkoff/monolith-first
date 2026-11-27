"""Tests of the choices of the theme kept in the database."""

import pytest

from server.apps.appearance.infra.themes import StoredThemes


@pytest.mark.django_db
def test_default_theme_is_current_before_a_choice() -> None:
    assert StoredThemes().current('classic') == 'classic'


@pytest.mark.django_db
def test_latest_choice_is_current() -> None:
    themes = StoredThemes()

    themes.keep('warm')
    themes.keep('bold')

    assert themes.current('classic') == 'bold'
