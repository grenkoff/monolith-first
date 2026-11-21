"""Creates a module of core with every layer: `make module NAME=<name>`."""

import ast
import re
import sys
from pathlib import Path
from typing import Final, final

_APPS: Final = Path('services/core/server/apps')
_SETTINGS: Final = Path('services/core/server/settings/components/common.py')
_NAME: Final = re.compile(r'^[a-z][a-z0-9_]*$')
_CHECK: Final = Path('services/core/scripts/modules.py')
_TECHNICAL: Final = '_TECHNICAL'
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
        if not _NAME.match(self._name) or self._name in self._technical():
            raise UnfitNameError(
                f'`{self._name}` is not the name of a business domain',
            )
        folder = self._root / _APPS / self._name
        if folder.exists():
            raise UnfitNameError(f'module `{self._name}` already exists')
        files = [folder / package / '__init__.py' for package in _PACKAGES]
        for path in files:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        models = folder / 'models.py'
        models.write_text(f'"""Database models of {self._name}."""\n')
        settings = self._root / _SETTINGS
        line = f"    'server.apps.{self._name}',\n"
        settings.write_text(
            _INSTALLED.sub(
                lambda found: found.group(0) + line,
                settings.read_text(),
                count=1,
            ),
        )
        return [*files, models]

    def _technical(self) -> frozenset[str]:
        """Returns the names of technical layers, as the module check lists them."""
        tree = ast.parse((self._root / _CHECK).read_text(encoding='utf-8'))
        for node in tree.body:
            if (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == _TECHNICAL
                and isinstance(node.value, ast.Call)
            ):
                return frozenset(ast.literal_eval(node.value.args[0]))
        return frozenset()


if __name__ == '__main__':
    try:
        files = Module(Path.cwd(), sys.argv[1] if len(sys.argv) > 1 else '').created()
    except UnfitNameError as error:
        sys.exit(f'scaffold: {error}')
    sys.stdout.write(''.join(f'created {path}\n' for path in files))
