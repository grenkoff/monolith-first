"""Tests of the report of services that share a database or face the world."""

from typing import Final

from scripts.compose import ComposeReport

_CORE: Final = 'core:dev'
_DB: Final = 'db'
_PORTS: Final = ({'target': 8000, 'published': '8000'},)


def _service(image: str, **settings: object) -> dict[str, object]:
    """Describes a resolved Compose service that runs an image."""
    return {'image': image, **settings}


def test_reports_published_ports_outside_core() -> None:
    services = {
        'core': _service(_CORE, ports=_PORTS),
        'hello': _service('hello:dev', ports=_PORTS),
    }

    problems = list(ComposeReport(services).problems())

    assert problems == ['hello publishes ports, but only core is public']


def test_reports_database_shared_by_two_services() -> None:
    services = {
        _DB: _service('postgres:18-alpine'),
        'core-migrate': _service(_CORE, depends_on={_DB: {}}),
        'core-events': _service(_CORE, depends_on={_DB: {}}),
        'billing': _service('billing:dev', depends_on={_DB: {}}),
    }

    problems = list(ComposeReport(services).problems())

    assert problems == ['db is shared by billing, core']
