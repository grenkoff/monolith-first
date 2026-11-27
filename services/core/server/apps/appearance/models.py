"""Database models of appearance."""

import uuid
from typing import Final, final, override

from django.db import models

_NAME_LENGTH: Final = 32


@final
class ThemeChoice(models.Model):
    """Theme of the site chosen by staff; the latest choice is in force."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(max_length=_NAME_LENGTH)

    @override
    def __str__(self) -> str:
        """Returns the name of the chosen theme."""
        return self.name
