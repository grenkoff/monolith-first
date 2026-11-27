"""Tests of the form in the header where staff choose the theme of the site."""

from http import HTTPStatus

import pytest
from django.test import Client

from tests.test_apps.test_appearance.test_views.themes import (
    CHOSEN,
    DEFAULT,
    DESIGN,
    choose,
    theme_of,
)


@pytest.mark.django_db
def test_default_theme_before_a_choice(client: Client) -> None:
    assert theme_of(client) == DEFAULT


def test_staff_return_to_the_page_they_chose_on(admin_client: Client) -> None:
    assert choose(admin_client, CHOSEN, DESIGN) == (HTTPStatus.FOUND, DESIGN)


def test_every_visitor_sees_the_theme_staff_chose(
    admin_client: Client,
    client: Client,
) -> None:
    choose(admin_client, CHOSEN)

    assert theme_of(client) == CHOSEN


def test_choice_never_leads_off_the_site(admin_client: Client) -> None:
    page = 'https://elsewhere.example/'

    assert choose(admin_client, CHOSEN, page) == (HTTPStatus.FOUND, '/')
