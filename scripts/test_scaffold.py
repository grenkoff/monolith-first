"""Tests of the generator of modules of core."""

from pathlib import Path

import pytest

from scaffold import Module, UnfitNameError

_SETTINGS = 'services/core/server/settings/components/common.py'
_APPS = """INSTALLED_APPS: tuple[str, ...] = (
    'server.apps.accounts',
    'server.apps.catalog',
    'server.common.outbox',
)
"""


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """Returns a project with the settings of core and one module."""
    settings = tmp_path / _SETTINGS
    settings.parent.mkdir(parents=True)
    settings.write_text(_APPS)
    (tmp_path / 'services/core/server/apps/catalog').mkdir(parents=True)
    check = tmp_path / 'services/core/scripts/modules.py'
    check.parent.mkdir(parents=True)
    check.write_text("_TECHNICAL: Final = frozenset(('auth', 'utils'))\n")
    return tmp_path


def test_module_gets_every_layer(project: Path) -> None:
    created = Module(project, 'bookings').created()

    apps = project / 'services/core/server/apps/bookings'
    assert sorted(path.relative_to(apps).as_posix() for path in created) == [
        '__init__.py',
        'api/__init__.py',
        'infra/__init__.py',
        'logic/__init__.py',
        'logic/usecases/__init__.py',
        'migrations/__init__.py',
        'models.py',
        'public/__init__.py',
        'views/__init__.py',
    ]
    assert (apps / 'models.py').read_text() == '"""Database models of bookings."""\n'


def test_module_is_installed_after_the_last_module(project: Path) -> None:
    Module(project, 'bookings').created()

    assert (project / _SETTINGS).read_text() == _APPS.replace(
        "    'server.apps.catalog',\n",
        "    'server.apps.catalog',\n    'server.apps.bookings',\n",
    )


@pytest.mark.parametrize('name', ['utils', 'auth', 'Bookings', '1st', 'my-module', ''])
def test_unfit_name_is_refused(project: Path, name: str) -> None:
    with pytest.raises(UnfitNameError):
        Module(project, name).created()


def test_existing_module_is_refused(project: Path) -> None:
    with pytest.raises(UnfitNameError, match='already exists'):
        Module(project, 'catalog').created()
