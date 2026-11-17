"""Loop that keeps a relay delivering until it is stopped."""

from typing import Protocol, final

import attrs


class Deliveries(Protocol):
    """Source of deliveries, one pending event at a time."""

    def deliver(self) -> bool:
        """Delivers one pending event; tells whether there was one."""


class Stop(Protocol):
    """Signal that asks a loop to stop."""

    def wait(self, timeout: float) -> bool:
        """Waits at most the timeout; tells whether the stop came."""


@final
@attrs.define(slots=True, frozen=True)
class Polling:
    """Delivers events and waits an interval whenever none is pending."""

    _relay: Deliveries
    _interval: float

    def run(self, stop: Stop) -> None:
        """Delivers until a stop comes while nothing is pending."""
