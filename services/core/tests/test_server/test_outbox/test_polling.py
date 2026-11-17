"""Tests of the loop that keeps the relay delivering until it is stopped."""

from typing import Final, final

import attrs

from server.common.outbox.polling import Polling

_INTERVAL: Final = 0.5


@final
@attrs.define(frozen=True)
class _Script:
    """Fake: relay and stop signal that answer as scripted and keep the waits."""

    _deliveries: list[bool]
    _stops: list[bool]
    waits: list[float] = attrs.field(factory=list)

    def deliver(self) -> bool:
        """Tells whether there was an event to deliver, as scripted."""
        return self._deliveries.pop(0)

    def wait(self, timeout: float) -> bool:
        """Keeps the timeout and tells whether a stop came, as scripted."""
        self.waits.append(timeout)
        return self._stops.pop(0)


def test_polling_waits_only_while_idle() -> None:
    script = _Script([False, True, False], [False, True])

    Polling(script, _INTERVAL).run(script)

    assert script.waits == [_INTERVAL, _INTERVAL]
