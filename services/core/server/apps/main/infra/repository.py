"""Database access for blog posts."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

import attrs

from server.apps.main.logic.value_objects import BlogPostCreatePayload
from server.apps.main.models import BlogPost

if TYPE_CHECKING:
    from uuid import UUID


@final
@attrs.define(slots=True, frozen=True)
class BlogPostRepo:
    """Repository for the ``BlogPost`` model."""

    def create(self, parsed_body: BlogPostCreatePayload) -> BlogPost:
        """Creates new ``BlogPost`` model."""
        return BlogPost.objects.create(
            title=parsed_body.title,
            body=parsed_body.body,
        )

    def get_by_id(self, blog_post_id: UUID) -> BlogPost:
        """Return ``BlogPost`` model by the primary key."""
        return BlogPost.objects.get(pk=blog_post_id)
