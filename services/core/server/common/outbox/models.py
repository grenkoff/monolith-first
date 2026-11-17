"""Database models of the outbox."""

import uuid
from typing import Final, final, override

from django.db import models

_TOPIC_MAX_LENGTH: Final = 200


@final
class Event(models.Model):
    """Fact written with the change it reports, kept until it is delivered."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    topic = models.CharField(max_length=_TOPIC_MAX_LENGTH)
    payload = models.JSONField()

    @override
    def __str__(self) -> str:
        """Returns the topic of the event."""
        return self.topic
