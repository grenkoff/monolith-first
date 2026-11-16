"""Tests of the report of modules that break the boundaries between modules."""

from pathlib import Path

from scripts.modules import ModuleTree


def _module(root: Path, name: str, *callees: str) -> None:
    """Writes a module whose infra imports the public packages of others."""
    infra = root / name / 'infra'
    infra.mkdir(parents=True)
    (infra / 'adapters.py').write_text(
        '\n'.join(
            f'from server.apps.{callee}.public import facade' for callee in callees
        ),
    )


def test_reports_call_chain_between_modules(tmp_path: Path) -> None:
    _module(tmp_path, 'billing', 'catalog')
    _module(tmp_path, 'catalog', 'pricing')
    _module(tmp_path, 'pricing')

    problems = list(ModuleTree(tmp_path).problems())

    assert problems == ['billing calls catalog, which calls pricing']
