"""Tests of the report of templates outside the design system."""

import pytest

from scripts.design import TemplateReport


def _template(text: str) -> list[str]:
    """Returns the problems of one template."""
    return list(TemplateReport({'page.html': text}).problems())


@pytest.mark.parametrize(
    'markup',
    [
        '<p class="text-gray-600">x</p>',
        '<p class="hover:bg-blue-500">x</p>',
        '<p class="text-white">x</p>',
        '<p class="mt-[13px]">x</p>',
        '<p class="bg-[#fff]">x</p>',
        '<p style="color: red">x</p>',
    ],
)
def test_off_system_markup_is_reported(markup: str) -> None:
    assert len(_template(markup)) == 1


def test_template_problem_names_the_file_and_line() -> None:
    assert _template('<main>\n<p class="text-red-700">x</p>') == [
        'page.html:2: `text-red-700` is outside the design system',
    ]


def test_style_attribute_is_named() -> None:
    assert _template('<p style="color: red">x</p>') == [
        'page.html:1: `style` is outside the design system',
    ]


def test_template_of_tokens_and_components_passes() -> None:
    markup = (
        '<p class="ds-card mt-4 grid gap-2 bg-surface text-ink-muted '
        'sm:grid-cols-2">x</p>'
    )
    assert not _template(markup)
