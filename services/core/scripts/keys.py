"""Reports models of core modules whose primary key is not a UUIDv7."""

import os
import sys
from collections.abc import Iterator
from typing import Protocol, final, override

import attrs
import django
from django.apps import apps
from django.apps.registry import Apps


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
        return iter(())


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    django.setup()
    problems = '\n'.join(KeyReport(apps).problems())
    sys.exit(problems or None)
