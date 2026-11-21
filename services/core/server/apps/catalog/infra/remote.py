"""Thumbnails made by the images service over gRPC."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, final

import attrs
import grpc

from server.apps.catalog.logic.constants import PHOTO_MAX_BYTES
from server.apps.catalog.logic.photos import (
    BrokenPhotoError,
    ThumbnailsUnavailableError,
)
from server.apps.catalog.logic.value_objects import Thumbnail
from server.contracts.images.v1 import images_pb2, images_pb2_grpc

if TYPE_CHECKING:
    from django.conf import LazySettings

_MESSAGE_LIMIT: Final = PHOTO_MAX_BYTES * 2


@final
@attrs.define(slots=True, frozen=True)
class RemoteThumbnails:
    """Adapter: asks the images service for thumbnails over gRPC."""

    _settings: LazySettings

    def made(self, image: bytes, width: int) -> Thumbnail:
        """Returns the thumbnail made by the images service, raising domain errors."""
        options = [
            ('grpc.max_send_message_length', _MESSAGE_LIMIT),
            ('grpc.max_receive_message_length', _MESSAGE_LIMIT),
        ]
        address = self._settings.IMAGES_GRPC_ADDR
        with grpc.insecure_channel(address, options=options) as channel:
            try:
                answer = images_pb2_grpc.ImagesServiceStub(channel).Thumbnail(
                    images_pb2.ThumbnailRequest(image=image, width=width),
                    timeout=self._settings.IMAGES_GRPC_TIMEOUT,
                )
            except grpc.RpcError as exc:
                if exc.code() == grpc.StatusCode.INVALID_ARGUMENT:
                    raise BrokenPhotoError(exc.details()) from exc
                raise ThumbnailsUnavailableError(str(exc)) from exc
        return Thumbnail(
            image=answer.image,
            width=answer.width,
            height=answer.height,
        )
