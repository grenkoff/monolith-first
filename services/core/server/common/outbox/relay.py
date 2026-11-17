"""Relay that delivers events from the outbox to their subscribers."""

from collections.abc import Mapping, Sequence
from typing import Protocol, final
from uuid import UUID

import attrs
from django.db import transaction

from server.common.outbox.models import Event


@final
@attrs.define(slots=True, frozen=True)
class Envelope:
    """Event as a subscriber receives it: its id and its payload."""

    id: UUID
    payload: object


class Subscriber(Protocol):
    """Module that reacts to the events of one topic."""

    def receive(self, envelope: Envelope) -> None:
        """Handles the event, at most once per event id."""


@final
@attrs.define(slots=True, frozen=True)
class Relay:
    """Delivers pending events to the subscribers of their topics."""

    _subscribers: Mapping[str, Sequence[Subscriber]]

    def deliver(self) -> bool:
        """Delivers and removes the oldest event; tells whether there was one."""
        with transaction.atomic():
            pending = Event.objects.select_for_update(skip_locked=True).order_by('id')
            for event in pending[:1]:
                for subscriber in self._subscribers.get(event.topic, ()):
                    subscriber.receive(Envelope(event.id, event.payload))
                event.delete()
                return True
        return False
