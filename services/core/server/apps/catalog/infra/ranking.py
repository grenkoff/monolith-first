"""Similarity of names computed by the Rust extension module."""

from collections.abc import Sequence
from typing import final

import attrs
import ranking


@final
@attrs.define(slots=True, frozen=True)
class RustSimilarity:
    """Adapter: the resemblance of names from the Rust module `ranking`."""

    def scores(self, query: str, names: Sequence[str]) -> list[float]:
        """Returns the resemblance of each name to the query, in the order given."""
        return ranking.Similarity(query)(list(names))
