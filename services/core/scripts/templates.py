"""Reports templates of a module that reach into the templates of another."""

import re
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path, PurePosixPath
from typing import Final, Protocol, final, override

import attrs

_ROOT: Final = Path('server')
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
class TemplateReport(Report):
    """Templates of modules that extend or include those of another module."""

    _templates: Mapping[str, str]

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per template of another module."""
        for name, text in self._templates.items():
            parts = PurePosixPath(name).parts
            if parts[:2] != ('server', 'apps'):
                continue
            allowed = _SHARED | {parts[2]}
            for found in _TAG.finditer(text):
                if found.group(1) not in allowed:
                    number = text.count('\n', 0, found.start()) + 1
                    yield (
                        f'{name}:{number}: a module uses only its own '
                        'templates and the site layout'
                    )


if __name__ == '__main__':
    templates = {
        str(path): path.read_text(encoding='utf-8')
        for path in sorted(_ROOT.glob('apps/*/templates/**/*.html'))
    }
    sys.exit('\n'.join(TemplateReport(templates).problems()) or None)
