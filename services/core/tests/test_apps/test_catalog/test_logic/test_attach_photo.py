"""Tests of the use case that attaches a photo to a product."""

from collections.abc import Sequence
from typing import final
from uuid import UUID, uuid7

import attrs
import pytest

from server.apps.catalog.logic.constants import THUMBNAIL_WIDTH
from server.apps.catalog.logic.photos import UnknownPhotoError
from server.apps.catalog.logic.usecases.attach_photo import AttachPhoto
from server.apps.catalog.logic.value_objects import (
    PhotoSize,
    PhotoUpload,
    Thumbnail,
)
from server.apps.catalog.public.products import Product, UnknownProductError

_TEA = Product(id=uuid7(), name='Green tea', price_cents=350, sold=0)


@final
@attrs.define(slots=True, frozen=True)
class _OneProduct:
    """Fake: a catalog of one product."""

    def product(self, identifier: UUID) -> Product:
        """Returns the product or raises UnknownProductError."""
        if identifier != _TEA.id:
            raise UnknownProductError(str(identifier))
        return _TEA


@final
@attrs.define(slots=True, frozen=True)
class _Halves:
    """Fake: thumbnails half as high as wide."""

    def made(self, image: bytes, width: int) -> Thumbnail:
        """Returns a made-up thumbnail of the width."""
        backwards = bytes(reversed(image))
        return Thumbnail(image=backwards, width=width, height=width // 2)


@final
@attrs.define(slots=True, frozen=True)
class _Album:
    """Fake: photos kept in a dictionary."""

    kept: dict[UUID, Thumbnail] = attrs.field(factory=dict)

    def keep(self, product: UUID, thumbnail: Thumbnail) -> None:
        """Keeps the thumbnail of the product."""
        self.kept[product] = thumbnail

    def thumbnail(self, product: UUID) -> Thumbnail:
        """Returns the kept thumbnail or raises UnknownPhotoError."""
        try:
            return self.kept[product]
        except KeyError as exc:
            raise UnknownPhotoError(str(product)) from exc

    def shown(self, products: Sequence[UUID]) -> frozenset[UUID]:
        """Returns the products that have a thumbnail."""
        return frozenset(products) & self.kept.keys()


def test_photo_becomes_a_thumbnail_of_the_product() -> None:
    album = _Album()

    size = AttachPhoto(_OneProduct(), _Halves(), album)(
        _TEA.id,
        PhotoUpload(image='cGhvdG8='),
    )

    assert size == PhotoSize(width=THUMBNAIL_WIDTH, height=THUMBNAIL_WIDTH // 2)
    assert album.thumbnail(_TEA.id) == Thumbnail(
        image=b'otohp',
        width=THUMBNAIL_WIDTH,
        height=THUMBNAIL_WIDTH // 2,
    )


def test_photo_of_an_unknown_product_is_refused() -> None:
    album = _Album()

    with pytest.raises(UnknownProductError):
        AttachPhoto(_OneProduct(), _Halves(), album)(
            uuid7(),
            PhotoUpload(image='cGhvdG8='),
        )

    assert not album.kept
