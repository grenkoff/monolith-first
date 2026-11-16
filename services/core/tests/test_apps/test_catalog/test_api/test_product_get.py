"""Tests of the product reading endpoint."""

import uuid
from http import HTTPStatus

import pytest
from django.urls import reverse
from dmr.test import DMRClient


@pytest.fixture
def product(dmr_client: DMRClient, db: None) -> dict[str, object]:
    """Puts a product on sale and returns it as the API answered."""
    answered: dict[str, object] = dmr_client.post(
        reverse('api:v1:catalog:product_create'),
        data={'name': 'Green tea', 'price_cents': 350},
    ).json()
    return answered


@pytest.mark.django_db
def test_product_read_by_id(
    dmr_client: DMRClient,
    product: dict[str, object],
) -> None:
    response = dmr_client.get(
        reverse('api:v1:catalog:product_get', kwargs={'id': product['id']}),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == product


@pytest.mark.django_db
def test_unknown_product_is_not_found(dmr_client: DMRClient) -> None:
    response = dmr_client.get(
        reverse('api:v1:catalog:product_get', kwargs={'id': uuid.uuid7()}),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': [{'msg': 'Product not found', 'type': 'not_found'}],
    }
