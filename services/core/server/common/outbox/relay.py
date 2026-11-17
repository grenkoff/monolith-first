"""Relay that delivers events from the outbox to their subscribers."""

from collections.abc import Mapping, Sequence
from typing import Protocol, final
from uuid import UUID

import attrs


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
        """Delivers the oldest pending event; tells whether there was one."""
        return False
