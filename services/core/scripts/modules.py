"""Reports modules of core that break the boundaries between modules."""

import ast
import re
import sys
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Final, Protocol, final, override

import attrs

_PUBLIC: Final = re.compile(r'server\.apps\.(?P<module>\w+)\.public\b')
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


class Report(Protocol):
    """Lists problems of some Python code."""

    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""


class Names(Protocol):
    """Names of modules that some Python code refers to."""

    def names(self) -> Iterator[str]:
        """Yields the names."""


@final
@attrs.define(slots=True, frozen=True)
class PublicImports(Names):
    """Modules whose public package some Python code imports."""

    _text: str

    @override
    def names(self) -> Iterator[str]:
        """Yields the module of each imported public package."""
        for node in ast.walk(ast.parse(self._text)):
            for source in self._sources(node):
                found = _PUBLIC.match(source)
                if found:
                    yield found['module']

    def _sources(self, node: ast.AST) -> Sequence[str]:
        """Returns the full names that an import statement brings in."""
        match node:
            case ast.Import(names=aliases):
                return [alias.name for alias in aliases]
            case ast.ImportFrom(module=str() as module, names=aliases):
                return [f'{module}.{alias.name}' for alias in aliases]
            case _:
                return []


@final
@attrs.define(slots=True, frozen=True)
class ModuleCalls(Names):
    """Other modules whose public packages one module imports."""

    _directory: Path

    @override
    def names(self) -> Iterator[str]:
        """Yields each called module once, in name order."""
        called = {
            name
            for path in self._directory.rglob('*.py')
            for name in PublicImports(path.read_text()).names()
        }
        yield from sorted(called - {self._directory.name})


@final
@attrs.define(slots=True, frozen=True)
class ChainReport(Report):
    """Calls of one module to modules that call further modules."""

    _caller: str
    _calls: Mapping[str, Sequence[str]]

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per chain that starts from the caller."""
        for callee in self._calls[self._caller]:
            yield from (
                f'{self._caller} calls {callee}, which calls {further}'
                for further in self._calls.get(callee, ())
            )


@final
@attrs.define(slots=True, frozen=True)
class NameReport(Report):
    """Name of a module that says what layer it is instead of what domain."""

    _name: str

    @override
    def problems(self) -> Iterator[str]:
        """Yields a line when the name belongs to a technical layer."""
        if self._name in _TECHNICAL:
            yield f'{self._name} is named after a technical layer, not a domain'


@final
@attrs.define(slots=True, frozen=True)
class ModuleTree(Report):
    """Boundary problems of the modules under a directory."""

    _root: Path

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""
        calls = {
            directory.name: tuple(ModuleCalls(directory).names())
            for directory in sorted(self._root.iterdir())
            if directory.is_dir() and not directory.name.startswith('_')
        }
        for caller in calls:
            yield from ChainReport(caller, calls).problems()
            yield from NameReport(caller).problems()


if __name__ == '__main__':
    problems = '\n'.join(ModuleTree(Path('server/apps')).problems())
    sys.exit(problems or None)
