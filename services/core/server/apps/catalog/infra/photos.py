"""Thumbnails kept in the database of the catalog."""

from collections.abc import Sequence
from typing import final
from uuid import UUID

import attrs

from server.apps.catalog import models
from server.apps.catalog.logic.photos import UnknownPhotoError
from server.apps.catalog.logic.value_objects import Thumbnail


@final
@attrs.define(slots=True, frozen=True)
class StoredPhotos:
    """Thumbnails kept in the tables of the catalog."""

    def keep(self, product: UUID, thumbnail: Thumbnail) -> None:
        """Keeps the thumbnail of the product, replacing an older one."""
        models.Photo.objects.update_or_create(
            product_id=product,
            defaults={
                'image': thumbnail.image,
                'width': thumbnail.width,
                'height': thumbnail.height,
            },
        )

    def thumbnail(self, product: UUID) -> Thumbnail:
        """Returns the thumbnail of the product or raises UnknownPhotoError."""
        try:
            stored = models.Photo.objects.get(product_id=product)
        except models.Photo.DoesNotExist as exc:
            raise UnknownPhotoError(str(product)) from exc
        return Thumbnail(
            image=bytes(stored.image),
            width=stored.width,
            height=stored.height,
        )

    def shown(self, products: Sequence[UUID]) -> frozenset[UUID]:
        """Returns those of the products that have a thumbnail."""
        return frozenset(
            models.Photo.objects.filter(product_id__in=products).values_list(
                'product_id',
                flat=True,
            ),
        )
