"""Tests of the choices of the theme in the admin."""

from http import HTTPStatus

from django.test import Client
from django.urls import reverse

from server.apps.appearance.models import ThemeChoice


def test_admin_lists_the_choices_of_the_theme(admin_client: Client) -> None:
    ThemeChoice.objects.create(name='bold')

    response = admin_client.get(
        reverse('admin:appearance_themechoice_changelist'),
    )

    assert 'bold' in response.content.decode()


def test_admin_never_adds_a_choice(admin_client: Client) -> None:
    response = admin_client.get(reverse('admin:appearance_themechoice_add'))

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_admin_never_rewrites_a_choice(admin_client: Client) -> None:
    choice = ThemeChoice.objects.create(name='warm')

    response = admin_client.post(
        reverse('admin:appearance_themechoice_change', args=[choice.pk]),
        {'name': 'neon'},
    )

    choice.refresh_from_db()
    assert (response.status_code, choice.name) == (HTTPStatus.FORBIDDEN, 'warm')
