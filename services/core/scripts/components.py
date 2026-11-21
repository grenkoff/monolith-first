"""Reports browser code that is not a web component of the project."""

import re
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path, PurePosixPath
from typing import Final, Protocol, final, override

import attrs

_ROOT: Final = Path('server')
_FOLDER: Final = 'components'
_FOREIGN: Final = re.compile(
    r'(?:\bfrom\s*|\bimport\s*\(\s*|^\s*import\s+)[\'"](?!\.{1,2}/)',
)
_TAG: Final = re.compile(r'<script\b([^>]*)>|\son[a-z]+\s*=')
_MODULE: Final = re.compile(
    r'type="module"\s+src="\{%\s*static\s+\'components/[\w-]+\.js\'\s*%\}"',
)


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
        for name, text in self._scripts.items():
            path = PurePosixPath(name)
            if path.parent.name != _FOLDER:
                yield f'{name}: JavaScript lives only in static/{_FOLDER}/'
                continue
            if f"customElements.define('{path.stem}'" not in text:
                yield f'{name}: defines no custom element named {path.stem}'
            for number, line in enumerate(text.splitlines(), start=1):
                if _FOREIGN.search(line):
                    yield f'{name}:{number}: imports from outside the project'


@final
@attrs.define(slots=True, frozen=True)
class ScriptReport(Report):
    """Templates that run scripts other than the components of the project."""

    _templates: Mapping[str, str]

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per inline, foreign or classic script."""
        for name, text in self._templates.items():
            for found in _TAG.finditer(text):
                attributes = found.group(1)
                if attributes is None or not _MODULE.search(attributes):
                    number = text.count('\n', 0, found.start()) + 1
                    yield (
                        f'{name}:{number}: scripts come only from '
                        f'static/{_FOLDER}/ as modules'
                    )


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
