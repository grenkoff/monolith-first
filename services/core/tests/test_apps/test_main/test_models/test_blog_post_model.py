"""Tests of the blog post model."""

from typing import final
from uuid import UUID

from hypothesis import given
from hypothesis.extra import django

from server.apps.main.models import BlogPost


def _version(identifier: object) -> int | None:
    """Returns the UUID version of an identifier, or nothing for anything else."""
    return identifier.version if isinstance(identifier, UUID) else None


@final
class TestBlogPost(django.TestCase):
    """This is a property-based test that ensures model correctness."""

    @given(django.from_model(BlogPost))
    def test_model_properties(self, instance: BlogPost) -> None:
        """Tests that instance can be saved and has correct representation."""
        instance.save()

        assert _version(instance.pk) == 7
        assert len(str(instance)) <= 20
