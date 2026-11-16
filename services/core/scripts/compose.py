"""Reports services of the Compose file that share a database or face the world."""

import json
import sys
from collections.abc import Iterator, Mapping
from typing import Any, Final, Protocol, final, override

import attrs

type _Services = Mapping[str, Mapping[str, Any]]

_PUBLIC: Final = 'core'
_DATABASE: Final = 'postgres'


class Report(Protocol):
    """Lists problems of some configuration."""

    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""


@final
@attrs.define(slots=True, frozen=True)
class Deployable:
    """What deploys a service: its image without a tag, or the service itself."""

    _name: str
    _service: Mapping[str, Any]

    @override
    def __str__(self) -> str:
        """Returns the image name without a tag, or the service name."""
        image = str(self._service.get('image', self._name))
        return image.partition(':')[0]


@final
@attrs.define(slots=True, frozen=True)
class PortReport(Report):
    """Ports that a service other than core publishes."""

    _name: str
    _service: Mapping[str, Any]

    @override
    def problems(self) -> Iterator[str]:
        """Yields a line when a service other than core publishes ports."""
        deployable = str(Deployable(self._name, self._service))
        if self._service.get('ports') and deployable != _PUBLIC:
            yield f'{self._name} publishes ports, but only {_PUBLIC} is public'


@final
@attrs.define(slots=True, frozen=True)
class DatabaseReport(Report):
    """Deployables that depend on one database service."""

    _database: str
    _services: _Services

    @override
    def problems(self) -> Iterator[str]:
        """Yields a line when more than one deployable uses the database."""
        users = sorted({
            str(Deployable(name, service))
            for name, service in self._services.items()
            if self._database in (service.get('depends_on') or {})
        })
        if len(users) > 1:
            names = ', '.join(users)
            yield f'{self._database} is shared by {names}'


@final
@attrs.define(slots=True, frozen=True)
class ComposeReport(Report):
    """Problems of the services of a resolved Compose file."""

    _services: _Services

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""
        for name, service in self._services.items():
            yield from PortReport(name, service).problems()
            if str(service.get('image', '')).startswith(_DATABASE):
                yield from DatabaseReport(name, self._services).problems()


if __name__ == '__main__':
    services = json.load(sys.stdin)['services']
    problems = '\n'.join(ComposeReport(services).problems())
    sys.exit(problems or None)
