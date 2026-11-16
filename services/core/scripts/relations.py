"""Reports model relations of core that reach the tables of another module."""

import os
import sys
from collections.abc import Iterator
from typing import Final, Protocol, final, override

import attrs
import django
from django.apps import apps
from django.apps.registry import Apps
from django.db.models import Model

_MODULES: Final = 'server.apps.'


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
        for model in self._registry.get_models():
            yield from ModelRelations(model).problems()


@final
@attrs.define(slots=True, frozen=True)
class ModelRelations(Report):
    """Relations that one model declares to models of other modules."""

    _model: type[Model]

    @override
    def problems(self) -> Iterator[str]:
        """Yields one line per declared relation that leaves the module."""
        options = self._model._meta
        for field in options.get_fields():
            target = field.related_model
            if field.auto_created or not isinstance(target, type):
                continue
            if Module(target).foreign_to(options.app_config.name):
                source = f'{options.label}.{field.name}'
                destination = target._meta.label
                yield f'{source} refers to {destination}'


@final
@attrs.define(slots=True, frozen=True)
class Module:
    """Module of core that a model belongs to."""

    _model: type[Model]

    def foreign_to(self, owner: str) -> bool:
        """Returns true when the model lives in a module other than the owner."""
        name = self._model._meta.app_config.name
        return name.startswith(_MODULES) and name != owner


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    django.setup()
    problems = '\n'.join(RelationReport(apps).problems())
    sys.exit(problems or None)
