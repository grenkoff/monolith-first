"""Tests of the blog post creation endpoint."""

from http import HTTPStatus
from typing import final
from uuid import UUID

import msgspec
import pytest
from django.urls import reverse
from dmr.test import DMRClient
from inline_snapshot import snapshot
from inline_snapshot_django import snapshot_queries
from polyfactory.factories.msgspec_factory import MsgspecFactory

from server.apps.main.logic.value_objects import (
    BlogPostCreatePayload,
    BlogPostFullPayload,
)
from server.apps.main.models import BlogPost


@final
class _BlogPostCreateFactory(MsgspecFactory[BlogPostCreatePayload]):
    """Builds random valid blog post payloads."""

    __check_model__ = True


def _version(identifier: object) -> int | None:
    """Returns the UUID version of an identifier, or nothing for anything else."""
    return identifier.version if isinstance(identifier, UUID) else None


@pytest.mark.django_db
def test_blog_post_create(dmr_client: DMRClient) -> None:
    """Ensures that blog posts can be created."""
    with snapshot_queries() as snap:
        response = dmr_client.post(
            reverse('api:v1:main:blog_post_create'),
            data=msgspec.to_builtins(_BlogPostCreateFactory.build()),
        )

    assert response.status_code == HTTPStatus.CREATED
    assert snap == snapshot([
        'INSERT INTO main_blogpost (...) VALUES (...) RETURNING ...',
    ])
    blog_post = msgspec.convert(response.json(), type=BlogPostFullPayload)
    assert _version(blog_post.id) == 7
    BlogPost.objects.get(pk=blog_post.id)
