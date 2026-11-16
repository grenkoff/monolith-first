"""Tests of the order placing endpoint."""

from http import HTTPStatus
from uuid import UUID, uuid7

import pytest
from django.urls import reverse
from dmr.test import DMRClient


def _draft(product: str, quantity: int) -> dict[str, object]:
    """Returns the request body that drafts an order."""
    return {'product': product, 'quantity': quantity}


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
    response = dmr_client.post(url, data=_draft(product, 3))

    assert response.status_code == HTTPStatus.CREATED
    order = response.json()
    assert UUID(order.pop('id')).version == 7
    assert order == {**_draft(product, 3), 'total_cents': 1050}


@pytest.mark.django_db
def test_unknown_product_is_a_conflict(dmr_client: DMRClient, url: str) -> None:
    response = dmr_client.post(url, data=_draft(str(uuid7()), 1))

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': [{'msg': 'Product is not on sale', 'type': 'user_msg'}],
    }


@pytest.mark.django_db
@pytest.mark.parametrize('quantity', [0, 101])
def test_order_rejects_quantity_out_of_range(
    dmr_client: DMRClient,
    url: str,
    product: str,
    quantity: int,
) -> None:
    response = dmr_client.post(url, data=_draft(product, quantity))

    assert response.status_code == HTTPStatus.BAD_REQUEST
