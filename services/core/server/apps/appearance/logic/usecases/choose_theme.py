"""Use case that chooses the theme of the whole site."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import attrs

from server.apps.appearance.logic.themes import UnknownThemeError

if TYPE_CHECKING:
    from server.apps.appearance.logic.themes import Themes


@final
@attrs.define(slots=True, frozen=True)
class ChooseTheme:
    """Chooses one of the themes of the site for every visitor."""

    _themes: Themes
    _names: tuple[str, ...]

    def __call__(self, name: str) -> None:
        """Keeps the theme as the choice of the site, or refuses an unknown one."""
        if name not in self._names:
            raise UnknownThemeError(name)
        self._themes.keep(name)
