"""Tests of the layout every page of the site shares."""

from http import HTTPStatus
from typing import Final

import pytest
from django.conf import LazySettings
from django.test import Client
from django.urls import reverse

from server.apps.catalog.models import Product

_SEARCH_LINK: Final = f'href="{reverse("catalog:search")}"'


@pytest.fixture
def example_pages(client: Client, db: None) -> dict[str, str]:
    """Puts a product on sale, orders it and returns the pages of the example."""
    tea = Product.objects.create(name='Green tea', price_cents=350)
    placed = client.post(
        reverse('orders:place'),
        {'product': str(tea.id), 'quantity': '1'},
    )
    return {
        'home': reverse('catalog:home'),
        'search': reverse('catalog:search'),
        'product': reverse('catalog:product', kwargs={'identifier': tea.id}),
        'order': placed['Location'],
    }


@pytest.mark.parametrize('page', ['home', 'search', 'product', 'order'])
def test_example_pages_show_the_site_navigation(
    client: Client,
    example_pages: dict[str, str],
    page: str,
) -> None:
    response = client.get(example_pages[page])

    header = response.content.decode().partition('</header>')[0]
    assert _SEARCH_LINK in header


@pytest.mark.django_db
def test_design_page_has_no_module_links(client: Client) -> None:
    response = client.get(reverse('design'))

    assert response.status_code == HTTPStatus.OK
    assert _SEARCH_LINK not in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fragment',
    [
        '<html lang="en"',
        'name="viewport"',
        '/static/site/site.css',
        '<header',
        '<main',
    ],
)
def test_pages_share_one_layout(client: Client, fragment: str) -> None:
    response = client.get(reverse('catalog:home'))

    assert fragment in response.content.decode()


@pytest.mark.django_db
def test_layout_names_the_site(client: Client, settings: LazySettings) -> None:
    settings.SITE_NAME = 'Tea house'

    response = client.get(reverse('catalog:home'))

    assert '<title>\n      Tea house\n    </title>' in response.content.decode()
