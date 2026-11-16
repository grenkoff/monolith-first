"""Tests of the product creation endpoint."""

from http import HTTPStatus
from uuid import UUID

import pytest
from django.urls import reverse
from dmr.test import DMRClient


@pytest.mark.django_db
def test_product_created_with_uuid7_id(dmr_client: DMRClient) -> None:
    response = dmr_client.post(
        reverse('api:v1:catalog:product_create'),
        data={'name': 'Green tea', 'price_cents': 350},
    )

    assert response.status_code == HTTPStatus.CREATED
    product = response.json()
    assert UUID(product.pop('id')).version == 7
    assert product == {'name': 'Green tea', 'price_cents': 350}
