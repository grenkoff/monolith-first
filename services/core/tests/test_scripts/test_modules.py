"""Tests of the report of modules that break the boundaries between modules."""

from pathlib import Path
from typing import Final

from scripts.modules import ModuleTree

_BILLING: Final = 'billing'
_CATALOG: Final = 'catalog'


def _module(root: Path, name: str, *callees: str) -> None:
    """Writes a module whose infra imports the public packages of others."""
    infra = root / name / 'infra'
    infra.mkdir(parents=True)
    (infra / 'adapters.py').write_text(
        '\n'.join(
            f'from server.apps.{callee}.public import facade' for callee in callees
        ),
    )


def _subscriber(root: Path, name: str, publisher: str) -> None:
    """Writes a module whose infra reads the events of another module."""
    (root / name / 'infra' / 'subscribers.py').write_text(
        f'from server.apps.{publisher}.public.events import Fact\n'
        f'from server.apps.{publisher}.public import events\n',
    )


def test_accepts_subscriptions_to_events(tmp_path: Path) -> None:
    _module(tmp_path, _BILLING, _CATALOG)
    _module(tmp_path, _CATALOG)
    _subscriber(tmp_path, _CATALOG, _BILLING)

    problems = list(ModuleTree(tmp_path).problems())

    assert not problems


def test_reports_call_chain_between_modules(tmp_path: Path) -> None:
    _module(tmp_path, _BILLING, _CATALOG)
    _module(tmp_path, _CATALOG, 'pricing')
    _module(tmp_path, 'pricing')

    problems = list(ModuleTree(tmp_path).problems())

    assert problems == ['billing calls catalog, which calls pricing']


def test_reports_cycle_between_modules(tmp_path: Path) -> None:
    _module(tmp_path, _BILLING, _CATALOG)
    _module(tmp_path, _CATALOG, _BILLING)

    problems = list(ModuleTree(tmp_path).problems())

    assert problems == [
        'billing calls catalog, which calls billing',
        'catalog calls billing, which calls catalog',
    ]


def test_reports_technical_module_names(tmp_path: Path) -> None:
    _module(tmp_path, _BILLING)
    _module(tmp_path, 'utils')

    problems = list(ModuleTree(tmp_path).problems())

    assert problems == ['utils is named after a technical layer, not a domain']
