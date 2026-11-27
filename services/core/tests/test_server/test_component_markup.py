"""Tests of the markup that web components enhance."""

from html.parser import HTMLParser
from typing import override

import pytest
from django.conf import LazySettings
from django.test import Client
from django.urls import reverse

from server.apps.catalog.models import Product

type _Tag = tuple[str, tuple[tuple[str, str | None], ...]]


class _Tags(HTMLParser):
    """Collects the start tags of a page with their attributes."""

    def __init__(self, page: str) -> None:
        """Reads the page."""
        super().__init__()
        self.found: list[_Tag] = []
        self.feed(page)

    @override
    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Keeps a start tag."""
        self.found.append((tag, tuple(attrs)))


def _tags(client: Client, url: str) -> list[_Tag]:
    """Returns the start tags of the page at the URL."""
    return _Tags(client.get(url).content.decode()).found


@pytest.mark.parametrize(
    'tag',
    [
        ('site-choice', ()),
        ('option', (('value', 'classic'), ('selected', None))),
        ('option', (('value', 'warm'),)),
        ('option', (('value', 'bold'),)),
        ('noscript', ()),
        (
            'script',
            (('type', 'module'), ('src', '/static/components/site-choice.js')),
        ),
    ],
)
def test_header_offers_staff_the_themes(
    admin_client: Client,
    settings: LazySettings,
    tag: _Tag,
) -> None:
    settings.SITE_THEME = 'classic'

    assert tag in _tags(admin_client, reverse('catalog:home'))


@pytest.mark.django_db
@pytest.mark.parametrize('element', ['site-choice', 'site-theme'])
def test_visitors_get_no_theme_switcher(client: Client, element: str) -> None:
    response = client.get(reverse('catalog:home'))

    assert element not in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'tag',
    [
        ('site-total', (('price-cents', '350'),)),
        ('output', (('name', 'total'),)),
        (
            'script',
            (('type', 'module'), ('src', '/static/components/site-total.js')),
        ),
    ],
)
def test_product_page_shows_a_live_total(client: Client, tag: _Tag) -> None:
    tea = Product.objects.create(name='Green tea', price_cents=350)

    url = reverse('catalog:product', kwargs={'identifier': tea.id})

    assert tag in _tags(client, url)
