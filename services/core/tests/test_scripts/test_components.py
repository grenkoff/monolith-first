"""Tests of the report of JavaScript files that are not web components."""

import pytest

from scripts.components import ComponentReport

_THEME = 'server/common/django/static/components/site-theme.js'
_DEFINED = "customElements.define('site-theme', SiteTheme);\n"


def _scripts(path: str, text: str) -> list[str]:
    """Returns the problems of one JavaScript file."""
    return list(ComponentReport({path: text}).problems())


def test_component_defining_its_element_passes() -> None:
    text = f"import {{ Price }} from './price.js';\n{_DEFINED}"
    assert not _scripts(_THEME, text)


def test_script_outside_components_is_reported() -> None:
    path = 'server/common/django/static/site/app.js'
    assert _scripts(path, _DEFINED) == [
        f'{path}: JavaScript lives only in static/components/',
    ]


def test_missing_element_is_reported() -> None:
    assert _scripts(_THEME, "customElements.define('site-other', Other);\n") == [
        f'{_THEME}: defines no custom element named site-theme',
    ]


@pytest.mark.parametrize(
    'statement',
    [
        "import { html } from 'lit';\n",
        "import { html } from 'https://cdn.example/lit.js';\n",
        "const lit = await import('lit');\n",
        "export * from 'lit';\n",
    ],
)
def test_foreign_import_is_reported(statement: str) -> None:
    assert _scripts(_THEME, f'{statement}{_DEFINED}') == [
        f'{_THEME}:1: imports from outside the project',
    ]
