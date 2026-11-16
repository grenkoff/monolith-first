"""Tests of the user model of accounts."""

from uuid import UUID

import pytest
from django.contrib.auth import get_user_model


def _version(identifier: object) -> int | None:
    """Returns the UUID version of an identifier, or nothing for anything else."""
    return identifier.version if isinstance(identifier, UUID) else None


def test_users_live_in_accounts() -> None:
    assert get_user_model()._meta.label == 'accounts.User'


@pytest.mark.django_db
def test_user_gets_uuid7_id() -> None:
    user = get_user_model().objects.create_user(username='reader')

    assert _version(user.pk) == 7
