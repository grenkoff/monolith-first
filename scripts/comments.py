"""Reports comments and tool directives on the lines a branch adds."""

from collections.abc import Iterator, Mapping
from typing import final


@final
class Additions:
    """Lines that a unified diff adds, by file."""

    def __init__(self, diff: str) -> None:
        """Keeps the text of the diff."""
        self._diff = diff

    def lines(self) -> dict[str, frozenset[int]]:
        """Returns the numbers of the added lines of every file."""
        return {}


@final
class Report:
    """Comments and tool directives on the added lines of files."""

    def __init__(
        self,
        texts: Mapping[str, str],
        added: Mapping[str, frozenset[int]],
    ) -> None:
        """Keeps the texts of the files and their added lines."""
        self._texts = texts
        self._added = added

    def problems(self) -> Iterator[str]:
        """Yields one line per comment or directive that was added."""
        yield from ()
