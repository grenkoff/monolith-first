"""Reports templates and themes that step outside the design system."""

import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Final, Protocol, final, override

import attrs

_TEMPLATES: Final = Path('server')
_THEMES: Final = Path('server/common/django/styles/themes.css')


class Report(Protocol):
    """Lists problems of some code."""

    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""


@final
@attrs.define(slots=True, frozen=True)
class TemplateReport(Report):
    """Templates that style a page past the tokens and components."""

    _templates: Mapping[str, str]

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per class or attribute outside the design system."""
        yield from (name for name in self._templates if not name)


@final
@attrs.define(slots=True, frozen=True)
class ThemeReport(Report):
    """Themes that miss a token or put text on a background it cannot be read on."""

    _css: str

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per missing token or low contrast."""
        yield from (line for line in self._css.splitlines() if not line)


if __name__ == '__main__':
    templates = {
        str(path): path.read_text(encoding='utf-8')
        for path in sorted(_TEMPLATES.glob('**/templates/**/*.html'))
    }
    problems = [
        *TemplateReport(templates).problems(),
        *ThemeReport(_THEMES.read_text(encoding='utf-8')).problems(),
    ]
    sys.exit('\n'.join(problems) or None)
