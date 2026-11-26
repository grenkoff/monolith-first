"""Tests of the thumbnails made by the images service over gRPC."""

import pytest
from django.conf import LazySettings

from server.apps.catalog.infra.remote import RemoteThumbnails
from server.apps.catalog.logic.photos import (
    BrokenPhotoError,
    ThumbnailsUnavailableError,
)
from server.apps.catalog.logic.value_objects import Thumbnail
from tests.plugins.images_server import BROKEN


@pytest.mark.usefixtures('images_server')
def test_images_service_makes_the_thumbnail(settings: LazySettings) -> None:
    made = RemoteThumbnails(settings).made(b'photo', 480)

    assert made == Thumbnail(image=b'thumbnail of photo', width=480, height=240)


@pytest.mark.usefixtures('images_server')
def test_broken_photo_is_refused(settings: LazySettings) -> None:
    with pytest.raises(BrokenPhotoError):
        RemoteThumbnails(settings).made(BROKEN, 480)


@pytest.mark.usefixtures('images_down')
def test_images_service_down_is_reported(settings: LazySettings) -> None:
    with pytest.raises(ThumbnailsUnavailableError):
        RemoteThumbnails(settings).made(b'photo', 480)
