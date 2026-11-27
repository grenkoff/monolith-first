"""Tests of the design system as pages carry and show it."""

import pytest
from django.conf import LazySettings
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize('theme', ['classic', 'warm', 'bold'])
def test_pages_carry_the_theme_of_the_site(
    client: Client,
    settings: LazySettings,
    theme: str,
) -> None:
    settings.SITE_THEME = theme

    response = client.get(reverse('catalog:home'))

    assert f'data-theme="{theme}"' in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fragment',
    [
        'data-theme="classic"',
        'data-theme="warm"',
        'data-theme="bold"',
        'class="ds-button"',
        'class="ds-button-quiet"',
        'ds-card',
        'ds-field',
        'ds-input',
        'ds-alert',
        'ds-heading',
        'ds-price',
    ],
)
def test_design_page_shows_every_component(
    client: Client,
    fragment: str,
) -> None:
    response = client.get(reverse('design'))

    assert fragment in response.content.decode()
