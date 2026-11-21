"""Tests of the search page of the catalog."""

from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from server.apps.catalog import models


@pytest.fixture
def shelf(db: None) -> None:
    """Puts green tea and black coffee on sale."""
    models.Product.objects.create(name='Green tea', price_cents=350)
    models.Product.objects.create(name='Black coffee', price_cents=1205)


@pytest.mark.usefixtures('shelf')
def test_search_finds_a_name_despite_a_typo(client: Client) -> None:
    response = client.get(reverse('catalog:search'), {'q': 'tee'})

    assert response.status_code == HTTPStatus.OK
    page = response.content.decode()
    assert 'Green tea' in page
    assert 'Black coffee' not in page


@pytest.mark.usefixtures('shelf')
def test_search_without_query_shows_only_the_form(client: Client) -> None:
    response = client.get(reverse('catalog:search'))

    page = response.content.decode()
    assert 'name="q"' in page
    assert 'Green tea' not in page
