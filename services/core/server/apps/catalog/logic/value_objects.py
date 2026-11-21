"""Value objects of the catalog."""

from typing import Annotated, final

import msgspec

from server.apps.catalog.logic.constants import (
    NAME_MAX_LENGTH,
    PHOTO_MAX_BYTES,
    PRICE_MAX_CENTS,
)
from server.common.text import VISIBLE_CHARACTER


@final
class ProductDraft(msgspec.Struct, frozen=True):
    """Product to put on sale: a visible name and a price in cents."""

    name: Annotated[
        str,
        msgspec.Meta(
            min_length=1,
            max_length=NAME_MAX_LENGTH,
            pattern=VISIBLE_CHARACTER,
        ),
    ]
    price_cents: Annotated[int, msgspec.Meta(ge=1, le=PRICE_MAX_CENTS)]


@final
class PhotoUpload(msgspec.Struct, frozen=True):
    """Photo of a product to make a thumbnail of: JPEG, PNG or WebP bytes."""

    image: Annotated[bytes, msgspec.Meta(min_length=1, max_length=PHOTO_MAX_BYTES)]


@final
class PhotoSize(msgspec.Struct, frozen=True):
    """Size in pixels of the thumbnail kept for a product."""

    width: int
    height: int


@final
class Thumbnail(msgspec.Struct, frozen=True):
    """Thumbnail of a photo: JPEG bytes and their size in pixels."""

    image: bytes
    width: int
    height: int
