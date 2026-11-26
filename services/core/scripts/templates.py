"""Reports templates of a module that reach into the templates of another."""

import re
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path, PurePosixPath
from typing import Final, Protocol, final, override

import attrs

_ROOT: Final = Path('server')
_MODULES: Final = ('server', 'apps')
_SHARED: Final = frozenset(('layout', 'site'))
_TAG: Final = re.compile(
    r'\{%-?\s*(?:extends|include)\s+[\'"]([^\'"/]+)/',
)


class Report(Protocol):
    """Lists problems of some code."""

    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""


@final
@attrs.define(slots=True, frozen=True)
class ModuleTemplate(Report):
    """One template that may extend or include those of another module."""

    _name: str
    _text: str

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per template of another module it uses."""
        parts = PurePosixPath(self._name).parts
        if parts[:2] != _MODULES:
            return
        allowed = _SHARED | {parts[len(_MODULES)]}
        for found in _TAG.finditer(self._text):
            if found.group(1) not in allowed:
                yield self._problem(found.start())

    def _problem(self, position: int) -> str:
        """Returns the line that reports the tag at the position."""
        number = self._text.count('\n', 0, position) + 1
        return (
            f'{self._name}:{number}: a module uses only its own '
            'templates and the site layout'
        )


@final
@attrs.define(slots=True, frozen=True)
class TemplateReport(Report):
    """Templates of modules that extend or include those of another module."""

    _templates: Mapping[str, str]

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per template of another module."""
        for name, text in self._templates.items():
            yield from ModuleTemplate(name, text).problems()


if __name__ == '__main__':
    templates = {
        str(path): path.read_text(encoding='utf-8')
        for path in sorted(_ROOT.glob('apps/*/templates/**/*.html'))
    }
    sys.exit('\n'.join(TemplateReport(templates).problems()) or None)
