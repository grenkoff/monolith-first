"""Tests of the report of model relations between modules."""

from typing import Any, Final

from django.apps.registry import Apps
from django.db import models

from scripts.relations import RelationReport

_CATALOG: Final = 'server.apps.catalog'
_GREETINGS: Final = 'server.apps.greetings'
_LABEL: Final = 'catalog'


def _model(registry: Apps, name: str, label: str, **fields: Any) -> type:
    """Declares a model of the app with the given label in a registry."""
    meta = type('Meta', (), {'app_label': label, 'apps': registry})
    return type(
        name,
        (models.Model,),
        {'__module__': f'{_CATALOG}.models', 'Meta': meta, **fields},
    )


def test_reports_relation_to_another_module() -> None:
    registry = Apps([_CATALOG, _GREETINGS])
    post = _model(registry, 'Post', _LABEL)
    _model(
        registry,
        'Greeting',
        'greetings',
        post=models.ForeignKey(post, on_delete=models.CASCADE),
    )

    problems = list(RelationReport(registry).problems())

    assert problems == ['greetings.Greeting.post refers to catalog.Post']


def test_accepts_relations_inside_a_module() -> None:
    registry = Apps([_CATALOG])
    post = _model(registry, 'Post', _LABEL)
    _model(
        registry,
        'Comment',
        _LABEL,
        post=models.ForeignKey(post, on_delete=models.CASCADE),
    )

    problems = list(RelationReport(registry).problems())

    assert not problems


def test_accepts_framework_relations_to_modules() -> None:
    registry = Apps([_CATALOG, 'django.contrib.admin'])
    post = _model(registry, 'Post', _LABEL)
    _model(
        registry,
        'Entry',
        'admin',
        post=models.ForeignKey(post, on_delete=models.CASCADE),
    )

    problems = list(RelationReport(registry).problems())

    assert not problems
