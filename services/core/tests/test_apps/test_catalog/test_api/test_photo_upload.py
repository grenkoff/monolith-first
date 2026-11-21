"""Tests of the validation of uploaded photos."""

from http import HTTPStatus

import pytest
from django.urls import reverse
from dmr.test import DMRClient

from server.apps.catalog import models
from server.apps.catalog.logic.constants import PHOTO_MAX_BASE64


@pytest.mark.django_db
@pytest.mark.parametrize(
    'image',
    [
        '',
        'abc',
        '@@@@',
        'A' * (PHOTO_MAX_BASE64 + 4),
    ],
)
def test_invalid_upload_is_refused(dmr_client: DMRClient, image: str) -> None:
    tea = models.Product.objects.create(name='Green tea', price_cents=350)

    response = dmr_client.put(
        reverse('api:v1:catalog:product_photo', kwargs={'id': tea.id}),
        data={'image': image},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
