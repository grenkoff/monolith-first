"""Interfaces of the search in the catalog."""

from collections.abc import Sequence
from typing import Protocol


class Similarity(Protocol):
    """Resemblance of names to a query, from 0 to 1."""

    def scores(self, query: str, names: Sequence[str]) -> list[float]:
        """Returns the resemblance of each name to the query, in the order given."""
