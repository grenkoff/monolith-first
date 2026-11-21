"""Tests of the pages of the catalog."""

import uuid
from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from server.apps.catalog import models


@pytest.fixture
def tea(db: None) -> models.Product:
    """Puts green tea on sale for 3.50."""
    return models.Product.objects.create(name='Green tea', price_cents=350)


@pytest.fixture
def coffee(db: None) -> models.Product:
    """Puts black coffee on sale for 12.05."""
    return models.Product.objects.create(name='Black coffee', price_cents=1205)


def test_home_lists_products_by_name(
    client: Client,
    tea: models.Product,
    coffee: models.Product,
) -> None:
    response = client.get(reverse('catalog:home'))

    assert response.status_code == HTTPStatus.OK
    page = response.content.decode()
    assert page.index('Black coffee') < page.index('Green tea')
    assert '12.05' in page
    assert '3.50' in page
    assert reverse('catalog:product', kwargs={'identifier': tea.id}) in page


@pytest.mark.django_db
def test_home_says_when_nothing_is_on_sale(client: Client) -> None:
    response = client.get(reverse('catalog:home'))

    assert response.status_code == HTTPStatus.OK
    assert 'Nothing is on sale yet' in response.content.decode()


def test_product_page_offers_an_order_form(
    client: Client,
    tea: models.Product,
) -> None:
    response = client.get(reverse('catalog:product', kwargs={'identifier': tea.id}))

    assert response.status_code == HTTPStatus.OK
    page = response.content.decode()
    assert 'Green tea' in page
    assert '3.50' in page
    assert f'name="product" value="{tea.id}"' in page
    assert 'name="quantity"' in page


@pytest.mark.django_db
def test_unknown_product_page_is_not_found(client: Client) -> None:
    response = client.get(
        reverse('catalog:product', kwargs={'identifier': uuid.uuid7()}),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
