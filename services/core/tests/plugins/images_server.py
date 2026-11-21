"""Fake images services for the tests of product photos."""

from collections.abc import Generator, Iterator
from concurrent import futures
from contextlib import contextmanager
from typing import Final, final, override

import grpc
import pytest
from django.conf import LazySettings

from server.contracts.images.v1 import images_pb2, images_pb2_grpc

BROKEN: Final = b'not a picture'
_GRACE: Final = 1


@final
class _FakeImages(images_pb2_grpc.ImagesServiceServicer):
    """Fake images service: a thumbnail half as high as wide, or a refusal."""

    @override
    def Thumbnail(
        self,
        request: images_pb2.ThumbnailRequest,
        context: grpc.ServicerContext,
    ) -> images_pb2.ThumbnailResponse:
        """Answers a made-up thumbnail, or aborts on a broken payload."""
        if request.image == BROKEN:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, 'not a picture')
        return images_pb2.ThumbnailResponse(
            image=b''.join((b'thumbnail of ', request.image)),
            width=request.width,
            height=request.width // 2,
        )


@contextmanager
def _serving() -> Generator[str]:
    """Serves the fake images service on a free local port."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    images_pb2_grpc.add_ImagesServiceServicer_to_server(_FakeImages(), server)
    port = server.add_insecure_port('127.0.0.1:0')
    server.start()
    try:
        yield f'127.0.0.1:{port}'
    finally:
        server.stop(grace=_GRACE).wait()


@pytest.fixture
def images_server(settings: LazySettings) -> Iterator[str]:
    """Points core at a fake images service."""
    with _serving() as address:
        settings.IMAGES_GRPC_ADDR = address
        yield address


@pytest.fixture
def images_down(settings: LazySettings) -> str:
    """Points core at an address where no images service listens."""
    address = '127.0.0.1:1'
    settings.IMAGES_GRPC_ADDR = address
    return address
