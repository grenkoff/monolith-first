"""Tests of the report of themes of the design system."""

from pathlib import Path
from typing import Final

from scripts.design import ThemeReport

_THEMES: Final = Path('server/common/django/styles/themes.css')

_GOOD_THEME: Final = """
[data-theme="plain"] {
  --ds-surface: #ffffff;
  --ds-surface-raised: #f8fafc;
  --ds-ink: #0f172a;
  --ds-ink-muted: #475569;
  --ds-line: #e2e8f0;
  --ds-accent: #1d4ed8;
  --ds-accent-ink: #ffffff;
  --ds-danger: #b91c1c;
  --ds-font-body: system-ui, sans-serif;
  --ds-font-heading: Georgia, serif;
  --ds-radius-control: 0.375rem;
  --ds-radius-card: 0.5rem;
  --ds-shadow-card: none;
}
"""


def test_complete_readable_theme_passes() -> None:
    assert not list(ThemeReport(_GOOD_THEME).problems())


def test_theme_without_a_token_is_reported() -> None:
    theme = _GOOD_THEME.replace('  --ds-danger: #b91c1c;\n', '')
    assert list(ThemeReport(theme).problems()) == [
        'theme plain has no token --ds-danger',
    ]


def test_theme_with_low_contrast_is_reported() -> None:
    theme = _GOOD_THEME.replace('--ds-ink-muted: #475569', '--ds-ink-muted: #cbd5e1')
    problems = list(ThemeReport(theme).problems())
    assert len(problems) == 1
    assert problems[0].startswith('theme plain: ink-muted on surface')


def test_no_theme_is_reported() -> None:
    assert list(ThemeReport('').problems()) == ['no theme is defined']


def test_themes_of_the_site_pass() -> None:
    themes = _THEMES.read_text(encoding='utf-8')
    assert not list(ThemeReport(themes).problems())
