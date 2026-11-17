"""Tests of the relay that delivers events from the outbox."""

from typing import Final, final
from uuid import UUID, uuid7

import attrs
import msgspec
import pytest

from server.common.outbox.models import Event
from server.common.outbox.outbox import StoredOutbox
from server.common.outbox.relay import Envelope, Relay

_TOPIC: Final = 'tests.v1.first'


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


@final
class _SubscriberError(RuntimeError):
    """Raised by a subscriber that cannot handle events."""

    __slots__ = ()


@final
@attrs.define(frozen=True)
class _Broken:
    """Fake: subscriber that fails on every event."""

    def receive(self, envelope: Envelope) -> None:
        """Fails to handle the envelope."""
        raise _SubscriberError(str(envelope.id))


@pytest.mark.django_db
def test_failed_delivery_leaves_the_event_pending() -> None:
    StoredOutbox().add(_TOPIC, _Fact(id=uuid7(), text='retried'))
    inbox = _Inbox()

    with pytest.raises(_SubscriberError):
        Relay({_TOPIC: (_Broken(),)}).deliver()

    assert Relay({_TOPIC: (inbox,)}).deliver()
    assert len(inbox.received) == 1


@pytest.mark.django_db
def test_relay_delivers_pending_events_by_topic() -> None:
    first = _Fact(id=uuid7(), text='first')
    StoredOutbox().add(_TOPIC, first)
    StoredOutbox().add('tests.v1.other', _Fact(id=uuid7(), text='other'))
    inbox = _Inbox()
    relay = Relay({_TOPIC: (inbox,)})

    deliveries = [relay.deliver() for _ in range(3)]

    assert deliveries == [True, True, False]
    assert inbox.received == [
        Envelope(first.id, {'id': str(first.id), 'text': 'first'}),
    ]
    assert not Event.objects.exists()
