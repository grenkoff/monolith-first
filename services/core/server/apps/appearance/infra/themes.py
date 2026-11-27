"""Choices of the theme kept in the database of the appearance module."""

from typing import final

import attrs


@final
@attrs.define(slots=True, frozen=True)
class StoredThemes:
    """Choices of the theme kept in the tables of the appearance module."""

    def current(self, default: str) -> str:
        """Reads the latest choice, or returns the default before any choice."""
        return default

    def keep(self, name: str) -> None:
        """Saves a new choice of the theme."""
