"""Tests of the sales the catalog learns from placed orders."""

import punq
import pytest
from django.urls import reverse
from dmr.test import DMRClient

from server.common.outbox.relay import Relay
from server.implemented import populate_dependencies


@pytest.mark.django_db
def test_product_shows_quantity_sold(dmr_client: DMRClient) -> None:
    product = dmr_client.post(
        reverse('api:v1:catalog:product_create'),
        data={'name': 'Green tea', 'price_cents': 350},
    ).json()
    dmr_client.post(
        reverse('api:v1:orders:order_create'),
        data={'product': product['id'], 'quantity': 3},
    )
    relay = populate_dependencies(punq.Container()).resolve(Relay)

    relay.deliver()
    response = dmr_client.get(
        reverse('api:v1:catalog:product_get', kwargs={'id': product['id']}),
    )

    assert response.json() == {**product, 'sold': 3}
