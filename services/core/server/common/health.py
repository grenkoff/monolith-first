"""Health endpoint of the HTTP API, outside every module."""

from typing import Literal, final

import msgspec
from dmr import Controller
from dmr.routing import Router, path

from server.common.serializers import StrictMsgspecSerializer


@final
class Health(msgspec.Struct, frozen=True):
    """State of the HTTP API: ok whenever it answers."""

    status: Literal['ok']


@final
class HealthGet(Controller[StrictMsgspecSerializer]):
    """Tells over HTTP that the API answers."""

    def get(self) -> Health:
        """Returns ok without touching the database."""
        return Health(status='ok')


router = Router(
    'health/',
    [path('', HealthGet.as_view(), name='health')],
)
