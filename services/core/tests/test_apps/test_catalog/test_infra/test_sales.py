"""Tests of the sales the catalog records from placed orders."""

from uuid import UUID, uuid7

import msgspec
import pytest
from django.urls import reverse
from dmr.test import DMRClient

from server.apps.catalog.infra.sales import RecordedSales
from server.apps.orders.public.events import OrderPlaced
from server.common.outbox.relay import Envelope


@pytest.mark.django_db
def test_same_event_counts_one_sale(dmr_client: DMRClient) -> None:
    product = dmr_client.post(
        reverse('api:v1:catalog:product_create'),
        data={'name': 'Green tea', 'price_cents': 350},
    ).json()
    placed = OrderPlaced(
        id=uuid7(),
        order=uuid7(),
        product=UUID(product['id']),
        quantity=2,
    )
    envelope = Envelope(placed.id, msgspec.to_builtins(placed))

    RecordedSales().receive(envelope)
    RecordedSales().receive(envelope)

    shown = dmr_client.get(
        reverse('api:v1:catalog:product_get', kwargs={'id': product['id']}),
    ).json()
    assert shown['sold'] == 2
