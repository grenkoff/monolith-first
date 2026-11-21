"""Resemblance of names to a query, computed in Rust."""

from typing import final

@final
class Similarity:
    """Adapter: a query whose resemblance to names is asked for."""

    def __init__(self, query: str) -> None:
        """Keeps the query."""

    def __call__(self, names: list[str]) -> list[float]:
        """Returns from 0 to 1 for each name, in the order given."""
