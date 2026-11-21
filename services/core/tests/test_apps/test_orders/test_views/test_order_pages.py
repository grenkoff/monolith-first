"""Tests of the pages of orders."""

import uuid
from http import HTTPStatus
from typing import Final

import pytest
from django.test import Client
from django.urls import reverse

from server.apps.catalog.models import Product
from server.apps.orders.models import Order

_PLACE: Final = reverse('orders:place')


def _form(product: object, quantity: str) -> dict[str, str]:
    """Returns the order form as a product page posts it."""
    return {'product': str(product), 'quantity': quantity}


@pytest.fixture
def tea(db: None) -> Product:
    """Puts green tea on sale for 3.50."""
    return Product.objects.create(name='Green tea', price_cents=350)


def test_order_form_places_the_order_and_shows_it(
    client: Client,
    tea: Product,
) -> None:
    response = client.post(_PLACE, _form(tea.id, '3'))

    assert response.status_code == HTTPStatus.FOUND
    assert response['Location'] == reverse(
        'orders:order',
        kwargs={'identifier': Order.objects.get().id},
    )


def test_order_page_shows_the_total_and_product(
    client: Client,
    tea: Product,
) -> None:
    placed = client.post(_PLACE, _form(tea.id, '3'), follow=True)

    assert placed.status_code == HTTPStatus.OK
    page = placed.content.decode()
    assert '10.50' in page
    assert 'Quantity: 3' in page
    assert reverse('catalog:product', kwargs={'identifier': tea.id}) in page


@pytest.mark.parametrize('quantity', ['0', '101', 'many', ''])
def test_quantity_out_of_range_is_refused(
    client: Client,
    tea: Product,
    quantity: str,
) -> None:
    response = client.post(_PLACE, _form(tea.id, quantity))

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'cannot be placed' in response.content.decode()
    assert not Order.objects.exists()


@pytest.mark.django_db
def test_order_of_an_unknown_product_is_refused(client: Client) -> None:
    response = client.post(_PLACE, _form(uuid.uuid7(), '1'))

    assert response.status_code == HTTPStatus.CONFLICT
    assert not Order.objects.exists()


@pytest.mark.django_db
def test_unknown_order_page_is_not_found(client: Client) -> None:
    response = client.get(
        reverse('orders:order', kwargs={'identifier': uuid.uuid7()}),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
