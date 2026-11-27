"""Use case that tells the theme every page is rendered in."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import attrs

if TYPE_CHECKING:
    from server.apps.appearance.logic.themes import Themes


@final
@attrs.define(slots=True, frozen=True)
class CurrentTheme:
    """Tells the theme of the site: the latest choice of staff or the default."""

    _themes: Themes
    _default: str

    def __call__(self) -> str:
        """Returns the name of the theme of the site."""
        return self._default
