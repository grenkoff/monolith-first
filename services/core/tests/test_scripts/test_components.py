"""Tests of the report of JavaScript files that are not web components."""

import pytest

from scripts.components import ComponentReport

_SAMPLE = 'server/common/django/static/components/site-sample.js'
_DEFINED = "customElements.define('site-sample', SiteSample);\n"


def _scripts(path: str, text: str) -> list[str]:
    """Returns the problems of one JavaScript file."""
    return list(ComponentReport({path: text}).problems())


def test_component_defining_its_element_passes() -> None:
    text = f"import {{ Price }} from './price.js';\n{_DEFINED}"
    assert not _scripts(_SAMPLE, text)


def test_script_outside_components_is_reported() -> None:
    path = 'server/common/django/static/site/app.js'
    assert _scripts(path, _DEFINED) == [
        f'{path}: JavaScript lives only in static/components/',
    ]


def test_missing_element_is_reported() -> None:
    assert _scripts(_SAMPLE, "customElements.define('site-other', Other);\n") == [
        f'{_SAMPLE}: defines no custom element named site-sample',
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
    assert _scripts(_SAMPLE, f'{statement}{_DEFINED}') == [
        f'{_SAMPLE}:1: imports from outside the project',
    ]
