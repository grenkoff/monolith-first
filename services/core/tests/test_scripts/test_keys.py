"""Tests of the report of models without a UUIDv7 primary key."""

import uuid
from typing import Final

from django.apps.registry import Apps
from django.db import models

from scripts.keys import KeyReport

_MAIN: Final = 'server.apps.main'


def _declare(registry: Apps, name: str, **fields: object) -> None:
    """Declares a model of the main app in a registry."""
    meta = type('Meta', (), {'app_label': 'main', 'apps': registry})
    namespace = {'__module__': f'{_MAIN}.models', 'Meta': meta}
    type(name, (models.Model,), {**namespace, **fields})


def test_reports_primary_key_other_than_uuid7() -> None:
    registry = Apps([_MAIN])
    _declare(registry, 'Counter')
    _declare(
        registry,
        'Random',
        id=models.UUIDField(primary_key=True, default=uuid.uuid4),
    )
    _declare(
        registry,
        'Post',
        id=models.UUIDField(primary_key=True, default=uuid.uuid7),
    )

    problems = list(KeyReport(registry).problems())

    assert problems == [
        'main.Counter has no UUIDv7 primary key',
        'main.Random has no UUIDv7 primary key',
    ]
