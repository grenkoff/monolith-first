"""Management command that delivers events from the outbox."""

import signal
import threading
from typing import final, override

from django.conf import settings
from django.core.management.base import BaseCommand

from server.common.di import HasContainer
from server.common.outbox.polling import Polling
from server.common.outbox.relay import Relay


@final
class Command(HasContainer, BaseCommand):
    """Delivers events from the outbox until the process receives SIGTERM."""

    help = 'Delivers events from the outbox to their subscribers until SIGTERM.'

    @override
    def handle(self, *args: object, **kwargs: object) -> None:
        """Relays events until SIGTERM, then delivers what is left and stops."""
        stopped = threading.Event()
        previous = signal.signal(signal.SIGTERM, lambda *_: stopped.set())
        self.stdout.write('relaying events')
        try:
            Polling(
                self.resolve(Relay),
                settings.OUTBOX_POLL_INTERVAL,
            ).run(stopped)
        finally:
            signal.signal(signal.SIGTERM, previous)
