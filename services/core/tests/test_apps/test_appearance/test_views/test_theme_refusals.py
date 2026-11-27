"""Tests of the theme form refusing whoever is not staff and unknown themes."""

from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from tests.test_apps.test_appearance.test_views.themes import (
    CHOSEN,
    DEFAULT,
    refused,
)


@pytest.mark.django_db
def test_visitors_cannot_choose_a_theme(client: Client) -> None:
    assert refused(client, CHOSEN) == (HTTPStatus.FORBIDDEN, DEFAULT)


@pytest.mark.django_db
def test_users_without_staff_rights_cannot_choose(client: Client) -> None:
    client.force_login(get_user_model().objects.create_user(username='guest'))

    assert refused(client, CHOSEN) == (HTTPStatus.FORBIDDEN, DEFAULT)


def test_unknown_theme_is_refused(admin_client: Client) -> None:
    assert refused(admin_client, 'neon') == (HTTPStatus.BAD_REQUEST, DEFAULT)
