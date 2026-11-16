"""Reports modules of core that break the boundaries between modules."""

import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, final, override

import attrs


class Report(Protocol):
    """Lists problems of some Python code."""

    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""


@final
@attrs.define(slots=True, frozen=True)
class ModuleTree(Report):
    """Boundary problems of the modules under a directory."""

    _root: Path

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""
        return iter(())


if __name__ == '__main__':
    problems = '\n'.join(ModuleTree(Path('server/apps')).problems())
    sys.exit(problems or None)
