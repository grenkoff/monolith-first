"""Tests of the report of templates that reach into another module."""

from typing import Final

import pytest

from scripts.templates import TemplateReport

_CATALOG: Final = 'server/apps/catalog/templates/catalog/page.html'


def _problems(name: str, text: str) -> list[str]:
    """Returns the problems of one template."""
    return list(TemplateReport({name: text}).problems())


@pytest.mark.parametrize('layout', ['site/layout.html', 'layout/base.html'])
def test_site_layout_may_be_extended(layout: str) -> None:
    assert not _problems(_CATALOG, f'{{% extends "{layout}" %}}')


def test_own_templates_may_be_included() -> None:
    assert not _problems(_CATALOG, '{% include "catalog/card.html" %}')


@pytest.mark.parametrize(
    'tag',
    [
        '{% extends "orders/order.html" %}',
        "{% include 'orders/summary.html' %}",
        '{%include "orders/summary.html" with total=1%}',
    ],
)
def test_template_of_another_module_is_reported(tag: str) -> None:
    assert _problems(_CATALOG, f'<p>Order</p>\n{tag}') == [
        f'{_CATALOG}:2: a module uses only its own templates and the site layout',
    ]


def test_link_to_another_module_passes() -> None:
    assert not _problems(_CATALOG, '<a href="{% url \'orders:place\' %}">Buy</a>')


@pytest.mark.parametrize(
    'name',
    [
        'server/templates/site/layout.html',
        'server/common/django/templates/design/index.html',
    ],
)
def test_templates_outside_modules_pass(name: str) -> None:
    assert not _problems(name, '{% include "orders/summary.html" %}')
