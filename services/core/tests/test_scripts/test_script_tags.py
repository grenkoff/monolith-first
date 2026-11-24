"""Tests of the report of scripts that templates run."""

import pytest

from scripts.components import ScriptReport


def _templates(text: str) -> list[str]:
    """Returns the problems of one template."""
    return list(ScriptReport({'page.html': text}).problems())


def test_module_script_of_a_component_passes() -> None:
    tag = (
        '<script type="module" '
        'src="{% static \'components/site-sample.js\' %}"></script>'
    )
    assert not _templates(tag)


@pytest.mark.parametrize(
    'markup',
    [
        '<script>alert(1)</script>',
        '<script src="https://cdn.example/htmx.js"></script>',
        '<script src="{% static \'components/site-sample.js\' %}"></script>',
        '<button onclick="go()">Go</button>',
    ],
)
def test_inline_or_foreign_script_is_reported(markup: str) -> None:
    assert _templates(markup) == [
        'page.html:1: scripts come only from static/components/ as modules',
    ]
