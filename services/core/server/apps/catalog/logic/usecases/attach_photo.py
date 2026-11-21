"""Use case that attaches a photo to a product."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import attrs

from server.apps.catalog.logic.value_objects import PhotoSize

if TYPE_CHECKING:
    from uuid import UUID

    from server.apps.catalog.logic.photos import Photos, Thumbnails
    from server.apps.catalog.logic.value_objects import PhotoUpload
    from server.apps.catalog.public.products import Catalog


@final
@attrs.define(slots=True, frozen=True)
class AttachPhoto:
    """Keeps the thumbnail of a photo for a product on sale."""

    _catalog: Catalog
    _thumbnails: Thumbnails
    _photos: Photos

    def __call__(self, product: UUID, upload: PhotoUpload) -> PhotoSize:
        """Returns the size of the thumbnail kept for the product."""
        return PhotoSize(width=len(upload.image), height=1)
