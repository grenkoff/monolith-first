"""Interfaces and errors of the photos of products."""

from collections.abc import Sequence
from typing import Protocol, final
from uuid import UUID

from server.apps.catalog.logic.value_objects import Thumbnail


@final
class BrokenPhotoError(ValueError):
    """Raised when a photo is not a picture the images service reads."""

    __slots__ = ()


@final
class ThumbnailsUnavailableError(ConnectionError):
    """Raised when no thumbnail can be made right now."""

    __slots__ = ()


@final
class UnknownPhotoError(LookupError):
    """Raised when a product has no photo."""

    __slots__ = ()


class Thumbnails(Protocol):
    """Source of thumbnails of photos."""

    def made(self, image: bytes, width: int) -> Thumbnail:
        """Returns the thumbnail of the photo, fitted to the width."""


class Photos(Protocol):
    """Thumbnails kept for the products of the catalog."""

    def keep(self, product: UUID, thumbnail: Thumbnail) -> None:
        """Keeps the thumbnail of the product, replacing an older one."""

    def thumbnail(self, product: UUID) -> Thumbnail:
        """Returns the thumbnail of the product or raises UnknownPhotoError."""

    def shown(self, products: Sequence[UUID]) -> frozenset[UUID]:
        """Returns those of the products that have a thumbnail."""
