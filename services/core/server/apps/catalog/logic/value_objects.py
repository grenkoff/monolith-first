"""Value objects of the catalog."""

from typing import Annotated, final

import msgspec

from server.apps.catalog.logic.constants import (
    NAME_MAX_LENGTH,
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
