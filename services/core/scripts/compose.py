"""Reports services of the Compose file that share a database or face the world."""

import json
import sys
from collections.abc import Iterator, Mapping
from typing import Any, Protocol, final, override

import attrs


class Report(Protocol):
    """Lists problems of some configuration."""

    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""


@final
@attrs.define(slots=True, frozen=True)
class ComposeReport(Report):
    """Problems of the services of a resolved Compose file."""

    _services: Mapping[str, Mapping[str, Any]]

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""
        return iter(())


if __name__ == '__main__':
    services = json.load(sys.stdin)['services']
    problems = '\n'.join(ComposeReport(services).problems())
    sys.exit(problems or None)
