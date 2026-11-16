"""Tests of the product creation endpoint."""

from http import HTTPStatus
from typing import Final
from uuid import UUID

import pytest
from django.urls import reverse
from dmr.test import DMRClient

_TEA: Final = 'Green tea'
_PRICE: Final = 350


def _draft(name: str, price_cents: int) -> dict[str, object]:
    """Returns the request body that drafts a product."""
    return {'name': name, 'price_cents': price_cents}


@pytest.fixture
def url() -> str:
    """Returns the URL of the product creation endpoint."""
    return reverse('api:v1:catalog:product_create')


@pytest.mark.django_db
def test_product_created_with_uuid7_id(dmr_client: DMRClient, url: str) -> None:
    response = dmr_client.post(url, data=_draft(_TEA, _PRICE))

    assert response.status_code == HTTPStatus.CREATED
    product = response.json()
    assert UUID(product.pop('id')).version == 7
    assert product == _draft(_TEA, _PRICE)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('name', 'price_cents'),
    [
        ('', _PRICE),
        ('   ', _PRICE),
        (chr(0x3000), _PRICE),
        ('x' * 101, _PRICE),
        (_TEA, 0),
        (_TEA, -1),
        (_TEA, 100_000_001),
    ],
)
def test_product_rejects_invalid_drafts(
    dmr_client: DMRClient,
    url: str,
    name: str,
    price_cents: int,
) -> None:
    response = dmr_client.post(url, data=_draft(name, price_cents))

    assert response.status_code == HTTPStatus.BAD_REQUEST
