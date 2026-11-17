"""Tests of the relay that delivers events from the outbox."""

from typing import final
from uuid import UUID, uuid7

import attrs
import msgspec
import pytest

from server.common.outbox.models import Event
from server.common.outbox.outbox import StoredOutbox
from server.common.outbox.relay import Envelope, Relay


@final
class _Fact(msgspec.Struct, frozen=True):
    """Fact of a test topic."""

    id: UUID
    text: str


@final
@attrs.define(frozen=True)
class _Inbox:
    """Fake: subscriber that keeps every envelope it receives."""

    received: list[Envelope] = attrs.field(factory=list)

    def receive(self, envelope: Envelope) -> None:
        """Keeps the envelope."""
        self.received.append(envelope)


@pytest.mark.django_db
def test_relay_delivers_pending_events_by_topic() -> None:
    first = _Fact(id=uuid7(), text='first')
    StoredOutbox().add('tests.v1.first', first)
    StoredOutbox().add('tests.v1.other', _Fact(id=uuid7(), text='other'))
    inbox = _Inbox()
    relay = Relay({'tests.v1.first': (inbox,)})

    deliveries = [relay.deliver() for _ in range(3)]

    assert deliveries == [True, True, False]
    assert inbox.received == [
        Envelope(first.id, {'id': str(first.id), 'text': 'first'}),
    ]
    assert not Event.objects.exists()
