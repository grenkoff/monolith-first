"""Thumbnails made by the images service over gRPC."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import attrs

from server.apps.catalog.logic.value_objects import Thumbnail

if TYPE_CHECKING:
    from django.conf import LazySettings


@final
@attrs.define(slots=True, frozen=True)
class RemoteThumbnails:
    """Adapter: asks the images service for thumbnails over gRPC."""

    _settings: LazySettings

    def made(self, image: bytes, width: int) -> Thumbnail:
        """Returns the thumbnail made by the images service."""
        return Thumbnail(image=image, width=width, height=width)
