"""Database models of the accounts module."""

import uuid
from typing import final

from django.contrib.auth.models import AbstractUser
from django.db import models


@final
class User(AbstractUser):
    """Person who signs in, known by a UUIDv7."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
