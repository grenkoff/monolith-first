"""Tests of the orders kept in the database."""

from uuid import uuid7

import pytest

from server.apps.orders.infra.orders import StoredOrders
from server.apps.orders.logic.orders import UnknownOrderError
from server.common.outbox.outbox import StoredOutbox


@pytest.mark.django_db
def test_unknown_order_error_names_the_id() -> None:
    identifier = uuid7()

    with pytest.raises(UnknownOrderError, match=str(identifier)):
        StoredOrders(StoredOutbox()).order(identifier)
