"""Creates a module of core with every layer: `make module NAME=<name>`."""

import re
import sys
from pathlib import Path
from typing import Final, final

_APPS: Final = Path('services/core/server/apps')
_SETTINGS: Final = Path('services/core/server/settings/components/common.py')
_NAME: Final = re.compile(r'^[a-z][a-z0-9_]*$')
_TECHNICAL: Final = frozenset((
    'api',
    'auth',
    'common',
    'core',
    'helpers',
    'infra',
    'logging',
    'shared',
    'utils',
))
_PACKAGES: Final = (
    '',
    'api',
    'infra',
    'logic',
    'logic/usecases',
    'migrations',
    'public',
    'views',
)
_INSTALLED: Final = re.compile(
    r"(?m)^    'server\.apps\.\w+',\n(?!    'server\.apps\.)",
)


@final
class UnfitNameError(ValueError):
    """Raised when a name cannot be the name of a new module."""

    __slots__ = ()


@final
class Module:
    """Module of core to create, named after a business domain."""

    def __init__(self, root: Path, name: str) -> None:
        """Keeps the root of the project and the name of the module."""
        self._root = root
        self._name = name

    def created(self) -> list[Path]:
        """Creates the packages of the module, installs it, returns the files."""
        return []


if __name__ == '__main__':
    try:
        files = Module(Path.cwd(), sys.argv[1] if len(sys.argv) > 1 else '').created()
    except UnfitNameError as error:
        sys.exit(f'scaffold: {error}')
    sys.stdout.write(''.join(f'created {path}\n' for path in files))
