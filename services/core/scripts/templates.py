"""Reports templates of a module that reach into the templates of another."""

from collections.abc import Iterator, Mapping
from typing import Protocol, final, override

import attrs


class Report(Protocol):
    """Lists problems of some code."""

    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""


@final
@attrs.define(slots=True, frozen=True)
class TemplateReport(Report):
    """Templates of modules that extend or include those of another module."""

    _templates: Mapping[str, str]

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per template of another module."""
        yield from ()
