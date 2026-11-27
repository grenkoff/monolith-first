"""Tests of the use cases that choose and tell the theme of the site."""

from typing import Final, final

import attrs
import pytest

from server.apps.appearance.logic.themes import UnknownThemeError
from server.apps.appearance.logic.usecases.choose_theme import ChooseTheme
from server.apps.appearance.logic.usecases.current_theme import CurrentTheme

_DEFAULT: Final = 'classic'
_NAMES: Final = (_DEFAULT, 'warm', 'bold')


@final
@attrs.define(slots=True, frozen=True)
class _Remembered:
    """Fake: choices of the theme kept in a list."""

    _choices: list[str] = attrs.field(factory=list)

    def current(self, default: str) -> str:
        """Returns the last choice, or the default before any choice."""
        return self._choices[-1] if self._choices else default

    def keep(self, name: str) -> None:
        """Appends the choice."""
        self._choices.append(name)


def test_default_theme_is_current_before_a_choice() -> None:
    assert CurrentTheme(_Remembered(), 'warm')() == 'warm'


def test_chosen_theme_becomes_current() -> None:
    themes = _Remembered()

    ChooseTheme(themes, _NAMES)('bold')

    assert CurrentTheme(themes, _DEFAULT)() == 'bold'


def test_unknown_theme_is_refused() -> None:
    themes = _Remembered()

    with pytest.raises(UnknownThemeError):
        ChooseTheme(themes, _NAMES)('neon')

    assert CurrentTheme(themes, _DEFAULT)() == _DEFAULT
