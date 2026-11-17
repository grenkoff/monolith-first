"""Tests of the command that relays events from the outbox."""

import io
import os
import signal
from typing import final, override
from uuid import UUID, uuid7

import msgspec
import pytest
from django.core.management import call_command

from server.common.outbox.models import Event
from server.common.outbox.outbox import StoredOutbox


@final
class _Fact(msgspec.Struct, frozen=True):
    """Fact of a topic nobody subscribes to."""

    id: UUID


@final
class _Terminating(io.StringIO):
    """Command output that sends SIGTERM to the process on the first write."""

    @override
    def write(self, text: str) -> int:
        """Keeps the text and asks the process to stop."""
        os.kill(os.getpid(), signal.SIGTERM)
        return super().write(text)


@pytest.mark.django_db
def test_relay_events_drains_outbox_on_sigterm() -> None:
    StoredOutbox().add('tests.v1.unheard', _Fact(id=uuid7()))

    call_command('relay_events', stdout=_Terminating())

    assert not Event.objects.exists()
