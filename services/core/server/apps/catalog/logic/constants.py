"""Business limits of the catalog."""

from typing import Final

NAME_MAX_LENGTH: Final = 100
PRICE_MAX_CENTS: Final = 100_000_000
RESEMBLANCE_MIN: Final = 0.5
THUMBNAIL_WIDTH: Final = 480
PHOTO_MAX_BYTES: Final = 16_777_216
