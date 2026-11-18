"""Tests of the products kept in the database of the catalog."""

from uuid import uuid7

import pytest

from server.apps.catalog.infra.products import StoredProducts
from server.apps.catalog.public.products import UnknownProductError


@pytest.mark.django_db
def test_unknown_product_error_names_the_id() -> None:
    identifier = uuid7()

    with pytest.raises(UnknownProductError, match=str(identifier)):
        StoredProducts().product(identifier)
