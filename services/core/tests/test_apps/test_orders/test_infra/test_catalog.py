"""Tests of the prices orders ask from the catalog facade."""

from uuid import uuid7

import pytest

from server.apps.catalog.infra.products import StoredProducts
from server.apps.orders.infra.catalog import CatalogPrices
from server.apps.orders.logic.orders import ProductNotOnSaleError


@pytest.mark.django_db
def test_product_not_on_sale_error_names_the_id() -> None:
    product = uuid7()

    with pytest.raises(ProductNotOnSaleError, match=str(product)):
        CatalogPrices(StoredProducts()).price_cents(product)
