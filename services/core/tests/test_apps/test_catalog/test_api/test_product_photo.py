"""Tests of the endpoint that attaches a photo to a product."""

import base64
import uuid
from http import HTTPStatus

import pytest
from django.urls import reverse
from dmr.test import DMRClient

from server.apps.catalog import models
from tests.plugins.images_server import BROKEN


def _upload(image: bytes) -> dict[str, str]:
    """Returns the request body that uploads a photo."""
    return {'image': base64.b64encode(image).decode()}


@pytest.fixture
def tea(db: None) -> models.Product:
    """Puts green tea on sale."""
    return models.Product.objects.create(name='Green tea', price_cents=350)


def _url(product: object) -> str:
    """Returns the photo endpoint of a product."""
    return reverse('api:v1:catalog:product_photo', kwargs={'id': product})


@pytest.mark.usefixtures('images_server')
def test_photo_is_kept_as_a_thumbnail(
    dmr_client: DMRClient,
    tea: models.Product,
) -> None:
    response = dmr_client.put(_url(tea.id), data=_upload(b'photo'))

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'width': 480, 'height': 240}
    assert bytes(models.Photo.objects.get(product=tea).image) == b'thumbnail of photo'


@pytest.mark.django_db
@pytest.mark.usefixtures('images_server')
def test_photo_of_an_unknown_product_is_not_found(dmr_client: DMRClient) -> None:
    response = dmr_client.put(_url(uuid.uuid7()), data=_upload(b'photo'))

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures('images_server')
def test_broken_photo_is_refused(
    dmr_client: DMRClient,
    tea: models.Product,
) -> None:
    response = dmr_client.put(_url(tea.id), data=_upload(BROKEN))

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert not models.Photo.objects.exists()


@pytest.mark.usefixtures('images_down')
def test_photo_waits_when_images_is_down(
    dmr_client: DMRClient,
    tea: models.Product,
) -> None:
    response = dmr_client.put(_url(tea.id), data=_upload(b'photo'))

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
