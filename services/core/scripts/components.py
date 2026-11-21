"""Reports browser code that is not a web component of the project."""

import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Final, Protocol, final, override

import attrs

_ROOT: Final = Path('server')


class Report(Protocol):
    """Lists problems of some code."""

    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""


@final
@attrs.define(slots=True, frozen=True)
class ComponentReport(Report):
    """JavaScript files that are not web components of the project."""

    _scripts: Mapping[str, str]

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per misplaced file, missing element or foreign import."""
        yield from (path for path in self._scripts if not path)


@final
@attrs.define(slots=True, frozen=True)
class ScriptReport(Report):
    """Templates that run scripts other than the components of the project."""

    _templates: Mapping[str, str]

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per inline, foreign or classic script."""
        yield from (path for path in self._templates if not path)


if __name__ == '__main__':
    scripts = {
        str(path): path.read_text(encoding='utf-8')
        for path in sorted(_ROOT.glob('**/static/**/*.js'))
    }
    templates = {
        str(path): path.read_text(encoding='utf-8')
        for path in sorted(_ROOT.glob('**/templates/**/*.html'))
    }
    problems = [
        *ComponentReport(scripts).problems(),
        *ScriptReport(templates).problems(),
    ]
    sys.exit('\n'.join(problems) or None)
