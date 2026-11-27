"""Shared steps of the tests of the theme form."""

from http import HTTPStatus
from typing import Final

from django.test import Client
from django.urls import reverse

DEFAULT: Final = 'classic'
CHOSEN: Final = 'bold'
DESIGN: Final = '/design/'


def choose(client: Client, theme: str, page: str = DESIGN) -> tuple[HTTPStatus, str]:
    """Sends the form with the theme and returns its status and where it leads."""
    response = client.post(
        reverse('appearance:theme'),
        {'theme': theme, 'next': page},
    )
    return HTTPStatus(response.status_code), response.get('Location', '')


def refused(client: Client, theme: str) -> tuple[HTTPStatus, str]:
    """Sends the form and returns its status with the theme of the site after it."""
    status, _ = choose(client, theme)
    return status, theme_of(client)


def theme_of(client: Client) -> str:
    """Returns the theme the home page is rendered in."""
    page = client.get(reverse('catalog:home')).content.decode()
    return page.partition('data-theme="')[2].partition('"')[0]
