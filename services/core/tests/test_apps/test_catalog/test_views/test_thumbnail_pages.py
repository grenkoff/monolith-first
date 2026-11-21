"""Tests of the thumbnails shown on the pages of the catalog."""

from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from server.apps.catalog import models


@pytest.fixture
def tea(db: None) -> models.Product:
    """Puts green tea on sale with a thumbnail."""
    product = models.Product.objects.create(name='Green tea', price_cents=350)
    models.Photo.objects.create(
        product=product,
        image=b'jpeg bytes',
        width=480,
        height=240,
    )
    return product


@pytest.fixture
def coffee(db: None) -> models.Product:
    """Puts black coffee on sale without a thumbnail."""
    return models.Product.objects.create(name='Black coffee', price_cents=1205)


def _thumbnail(product: models.Product) -> str:
    """Returns the address of the thumbnail of a product."""
    return reverse('catalog:thumbnail', kwargs={'identifier': product.id})


def test_thumbnail_is_served_as_jpeg(client: Client, tea: models.Product) -> None:
    response = client.get(_thumbnail(tea))

    assert response.status_code == HTTPStatus.OK
    assert response['Content-Type'] == 'image/jpeg'
    assert response.content == b'jpeg bytes'


def test_missing_thumbnail_is_not_found(
    client: Client,
    coffee: models.Product,
) -> None:
    assert client.get(_thumbnail(coffee)).status_code == HTTPStatus.NOT_FOUND


def test_pages_show_only_existing_thumbnails(
    client: Client,
    tea: models.Product,
    coffee: models.Product,
) -> None:
    home = client.get(reverse('catalog:home')).content.decode()
    page = client.get(
        reverse('catalog:product', kwargs={'identifier': tea.id}),
    ).content.decode()

    assert _thumbnail(tea) in home
    assert _thumbnail(coffee) not in home
    assert _thumbnail(tea) in page
