"""Interfaces and errors of the appearance of the site."""

from typing import Protocol, final


@final
class UnknownThemeError(ValueError):
    """Raised when a theme is not one of the themes of the site."""

    __slots__ = ()


class Themes(Protocol):
    """Themes chosen by staff, kept by appearance."""

    def current(self, default: str) -> str:
        """Returns the latest choice, or the default before any choice."""

    def keep(self, name: str) -> None:
        """Keeps a choice of the theme."""
