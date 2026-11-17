"""Tests of the order reading endpoint."""

from http import HTTPStatus
from uuid import uuid7

import pytest
from django.urls import reverse
from dmr.test import DMRClient


def _url(identifier: object) -> str:
    """Returns the URL of the order with the id."""
    return reverse('api:v1:orders:order_get', kwargs={'id': identifier})


@pytest.fixture
def order(dmr_client: DMRClient, db: None) -> dict[str, object]:
    """Places an order for a product on sale and returns it as answered."""
    product = dmr_client.post(
        reverse('api:v1:catalog:product_create'),
        data={'name': 'Green tea', 'price_cents': 350},
    ).json()
    answered: dict[str, object] = dmr_client.post(
        reverse('api:v1:orders:order_create'),
        data={'product': product['id'], 'quantity': 2},
    ).json()
    return answered


@pytest.mark.django_db
def test_order_read_by_id(
    dmr_client: DMRClient,
    order: dict[str, object],
) -> None:
    response = dmr_client.get(_url(order['id']))

    assert response.status_code == HTTPStatus.OK
    assert response.json() == order


@pytest.mark.django_db
def test_unknown_order_is_not_found(dmr_client: DMRClient) -> None:
    response = dmr_client.get(_url(uuid7()))

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': [{'msg': 'Order not found', 'type': 'not_found'}],
    }
