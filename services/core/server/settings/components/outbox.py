"""Settings of the relay that delivers events from the outbox."""

from server.settings.components import config

OUTBOX_POLL_INTERVAL = config('OUTBOX_POLL_INTERVAL', cast=float, default=1.0)
