"""Management command that delivers events from the outbox."""

import signal
import threading
from typing import final, override

from django.core.management.base import BaseCommand


@final
class Command(BaseCommand):
    """Delivers events from the outbox until the process receives SIGTERM."""

    help = 'Delivers events from the outbox to their subscribers until SIGTERM.'

    @override
    def handle(self, *args: object, **kwargs: object) -> None:
        """Relays events until SIGTERM, then delivers what is left and stops."""
        stopped = threading.Event()
        signal.signal(signal.SIGTERM, lambda *_: stopped.set())
        self.stdout.write('relaying events')
