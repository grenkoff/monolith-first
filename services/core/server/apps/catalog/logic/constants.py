"""Business limits of the catalog."""

from typing import Final

NAME_MAX_LENGTH: Final = 100
PRICE_MAX_CENTS: Final = 100_000_000
RESEMBLANCE_MIN: Final = 0.5
THUMBNAIL_WIDTH: Final = 480
PHOTO_MAX_BYTES: Final = 8_388_608
PHOTO_MAX_BASE64: Final = 11_184_812
BASE64: Final = r'^(?:[A-Za-z0-9+/]{4})+(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'
