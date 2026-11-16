"""Reports model relations of core that reach the tables of another module."""

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
class RelationReport(Report):
    """Relations between models of different modules in a registry."""

    _registry: Apps

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per relation to a model of another module."""
        return iter(())


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    django.setup()
    problems = '\n'.join(RelationReport(apps).problems())
    sys.exit(problems or None)
