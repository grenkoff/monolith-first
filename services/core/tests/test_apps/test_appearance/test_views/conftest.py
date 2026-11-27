"""Fixtures of the tests of the theme form."""

import pytest
from django.conf import LazySettings

from tests.test_apps.test_appearance.test_views.themes import DEFAULT


@pytest.fixture(autouse=True)
def _default_theme(settings: LazySettings) -> None:
    """Makes classic the theme of the site before any choice."""
    settings.SITE_THEME = DEFAULT
