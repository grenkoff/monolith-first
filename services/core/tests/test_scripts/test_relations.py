"""Tests of the report of model relations between modules."""

from typing import Any, Final

from django.apps.registry import Apps
from django.db import models

from scripts.relations import RelationReport

_MAIN: Final = 'server.apps.main'
_GREETINGS: Final = 'server.apps.greetings'


def _model(registry: Apps, name: str, label: str, **fields: Any) -> type:
    """Declares a model of the app with the given label in a registry."""
    meta = type('Meta', (), {'app_label': label, 'apps': registry})
    return type(
        name,
        (models.Model,),
        {'__module__': f'{_MAIN}.models', 'Meta': meta, **fields},
    )


def test_reports_relation_to_another_module() -> None:
    registry = Apps([_MAIN, _GREETINGS])
    post = _model(registry, 'Post', 'main')
    _model(
        registry,
        'Greeting',
        'greetings',
        post=models.ForeignKey(post, on_delete=models.CASCADE),
    )

    problems = list(RelationReport(registry).problems())

    assert problems == ['greetings.Greeting.post refers to main.Post']


def test_accepts_relations_inside_a_module() -> None:
    registry = Apps([_MAIN])
    post = _model(registry, 'Post', 'main')
    _model(
        registry,
        'Comment',
        'main',
        post=models.ForeignKey(post, on_delete=models.CASCADE),
    )

    problems = list(RelationReport(registry).problems())

    assert not problems
