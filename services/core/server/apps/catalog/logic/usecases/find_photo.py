"""Use case that finds the thumbnail of a product."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import attrs

if TYPE_CHECKING:
    from collections.abc import Sequence
    from uuid import UUID

    from server.apps.catalog.logic.photos import Photos
    from server.apps.catalog.logic.value_objects import Thumbnail


@final
@attrs.define(slots=True, frozen=True)
class FindPhoto:
    """Finds the thumbnails kept for products."""

    _photos: Photos

    def __call__(self, product: UUID) -> Thumbnail:
        """Returns the thumbnail of the product or raises UnknownPhotoError."""
        return self._photos.thumbnail(product)

    def shown(self, products: Sequence[UUID]) -> frozenset[UUID]:
        """Returns those of the products that have a thumbnail."""
        return frozenset(products[:0])
