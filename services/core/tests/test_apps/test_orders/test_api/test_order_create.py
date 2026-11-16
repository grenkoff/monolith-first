"""Tests of the order placing endpoint."""

from http import HTTPStatus
from uuid import UUID

import pytest
from django.urls import reverse
from dmr.test import DMRClient


@pytest.fixture
def url() -> str:
    """Returns the URL of the order placing endpoint."""
    return reverse('api:v1:orders:order_create')


@pytest.fixture
def product(dmr_client: DMRClient, db: None) -> str:
    """Puts a product on sale for 350 cents and returns its id."""
    answered = dmr_client.post(
        reverse('api:v1:catalog:product_create'),
        data={'name': 'Green tea', 'price_cents': 350},
    ).json()
    identifier: str = answered['id']
    return identifier


@pytest.mark.django_db
def test_order_placed_at_catalog_price(
    dmr_client: DMRClient,
    url: str,
    product: str,
) -> None:
    response = dmr_client.post(url, data={'product': product, 'quantity': 3})

    assert response.status_code == HTTPStatus.CREATED
    order = response.json()
    assert UUID(order.pop('id')).version == 7
    assert order == {'product': product, 'quantity': 3, 'total_cents': 1050}
