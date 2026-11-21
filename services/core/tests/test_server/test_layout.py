"""Tests of the layout every page of the site shares."""

import pytest
from django.conf import LazySettings
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fragment',
    [
        '<html lang="en"',
        'name="viewport"',
        '/static/site/site.css',
        '<header',
        '<main',
    ],
)
def test_pages_share_one_layout(client: Client, fragment: str) -> None:
    response = client.get(reverse('catalog:home'))

    assert fragment in response.content.decode()


@pytest.mark.django_db
def test_layout_names_the_site(client: Client, settings: LazySettings) -> None:
    settings.SITE_NAME = 'Tea house'

    response = client.get(reverse('catalog:home'))

    assert '<title>\n      Tea house\n    </title>' in response.content.decode()
