"""Reports models of core modules whose primary key is not a UUIDv7."""

import os
import sys
import uuid
from collections.abc import Iterator
from typing import Final, Protocol, final, override

import attrs
import django
from django.apps import apps
from django.apps.registry import Apps
from django.db.models import UUIDField

_MODULES: Final = 'server.apps.'


class Report(Protocol):
    """Lists problems of some code."""

    def problems(self) -> Iterator[str]:
        """Yields one line per problem."""


@final
@attrs.define(slots=True, frozen=True)
class KeyReport(Report):
    """Models of modules in a registry whose primary key is not a UUIDv7."""

    _registry: Apps

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per model without a UUIDv7 primary key."""
        for model in self._registry.get_models():
            options = model._meta
            key = options.pk
            if not options.app_config.name.startswith(_MODULES):
                continue
            if not isinstance(key, UUIDField) or key.default is not uuid.uuid7:
                yield f'{options.label} has no UUIDv7 primary key'


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    django.setup()
    problems = '\n'.join(KeyReport(apps).problems())
    sys.exit(problems or None)
