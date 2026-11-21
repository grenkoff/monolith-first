"""Reports templates and themes that step outside the design system."""

import re
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Final, Protocol, final, override

import attrs

_TEMPLATES: Final = Path('server')
_THEMES: Final = Path('server/common/django/styles/themes.css')

_PALETTE: Final = (
    'slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|'
    'teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose|black|white'
)
_UTILITIES: Final = (
    'bg|text|border|ring|outline|fill|stroke|from|via|to|divide|placeholder|'
    'decoration|shadow|accent|caret'
)
_PALETTE_CLASS: Final = re.compile(
    rf'^(?:[\w-]+:)*(?:{_UTILITIES})(?:-[xytrbl])?-(?:{_PALETTE})(?:-\d+)?(?:/\d+)?$',
)
_ARBITRARY: Final = re.compile(r'\[.*\]')
_CLASSES: Final = re.compile(r'class="([^"]*)"')
_STYLE: Final = re.compile(r'\sstyle\s*=')

_THEME: Final = re.compile(r'\[data-theme="([\w-]+)"\]\s*\{([^}]*)\}')
_TOKEN: Final = re.compile(r'--ds-([\w-]+):\s*([^;]+);')
_SURFACE: Final = 'surface'
_RAISED: Final = 'surface-raised'
_INK: Final = 'ink'
_MUTED: Final = 'ink-muted'
_ACCENT: Final = 'accent'
_ACCENT_INK: Final = 'accent-ink'
_DANGER: Final = 'danger'
_TOKENS: Final = (
    _SURFACE,
    _RAISED,
    _INK,
    _MUTED,
    'line',
    _ACCENT,
    _ACCENT_INK,
    _DANGER,
    'font-body',
    'font-heading',
    'radius-control',
    'radius-card',
    'shadow-card',
)
_READABLE: Final = 4.5
_PAIRS: Final = (
    (_INK, _SURFACE),
    (_INK, _RAISED),
    (_MUTED, _SURFACE),
    (_ACCENT, _SURFACE),
    (_ACCENT_INK, _ACCENT),
    (_DANGER, _SURFACE),
)
_CHANNEL: Final = 255
_LINEAR_EDGE: Final = 10
_DIGITS: Final = 2
_LINEAR_SLOPE: Final = 12.92
_GAMMA_OFFSET: Final = 0.055
_GAMMA_SCALE: Final = 1.055
_GAMMA: Final = 2.4
_WEIGHTS: Final = (0.2126, 0.7152, 0.0722)
_FLARE: Final = 0.05


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
        for name, text in self._templates.items():
            for number, line in enumerate(text.splitlines(), start=1):
                for token in self._outsiders(line):
                    yield f'{name}:{number}: `{token}` is outside the design system'

    def _outsiders(self, line: str) -> Iterator[str]:
        """Yields the classes and attributes of a line that bypass the tokens."""
        if _STYLE.search(line):
            yield 'style'
        for classes in _CLASSES.findall(line):
            yield from (
                name
                for name in classes.split()
                if _PALETTE_CLASS.match(name) or _ARBITRARY.search(name)
            )


class Shade(Protocol):
    """Colour that has a relative luminance."""

    def luminance(self) -> float:
        """Returns the relative luminance, from 0 for black to 1 for white."""

    def contrast(self, other: Shade) -> float:
        """Returns the WCAG contrast ratio between this and another colour."""


@final
@attrs.define(slots=True, frozen=True)
class Colour(Shade):
    """Colour of a token, written as #rrggbb."""

    _hex: str

    @override
    def contrast(self, other: Shade) -> float:
        """Returns the WCAG contrast ratio between two colours."""
        lighter, darker = sorted(
            (self.luminance(), other.luminance()),
            reverse=True,
        )
        return (lighter + _FLARE) / (darker + _FLARE)

    @override
    def luminance(self) -> float:
        """Returns the relative luminance of the colour."""
        channels = bytes.fromhex(self._hex[1:])
        linear = (self._linear(channel) for channel in channels)
        return sum(
            weight * channel for weight, channel in zip(_WEIGHTS, linear, strict=True)
        )

    def _linear(self, channel: int) -> float:
        """Returns a channel from 0 to 255 converted from sRGB to linear light."""
        share = channel / _CHANNEL
        if channel <= _LINEAR_EDGE:
            return share / _LINEAR_SLOPE
        return float(((share + _GAMMA_OFFSET) / _GAMMA_SCALE) ** _GAMMA)


@final
@attrs.define(slots=True, frozen=True)
class ThemeReport(Report):
    """Themes that miss a token or put text on a background it cannot be read on."""

    _css: str

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per missing token or low contrast."""
        themes = _THEME.findall(self._css)
        if not themes:
            yield 'no theme is defined'
        for name, body in themes:
            tokens = dict(_TOKEN.findall(body))
            for token in _TOKENS:
                if token not in tokens:
                    yield f'theme {name} has no token --ds-{token}'
            yield from self._unreadable(name, tokens)

    def _unreadable(self, name: str, tokens: Mapping[str, str]) -> Iterator[str]:
        """Yields one line per pair of colours below the readable contrast."""
        for text, background in _PAIRS:
            if text not in tokens or background not in tokens:
                continue
            ratio = round(
                Colour(tokens[text]).contrast(Colour(tokens[background])),
                _DIGITS,
            )
            if ratio < _READABLE:
                yield (
                    f'theme {name}: {text} on {background} has contrast '
                    f'{ratio:.2f}, at least {_READABLE}'
                )


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
