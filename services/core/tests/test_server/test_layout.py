"""Tests of the layout every page of the site shares."""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'fragment',
    [
        '<html lang="en">',
        'name="viewport"',
        '/static/site/site.css',
        '<header',
        '<main',
    ],
)
def test_pages_share_one_layout(client: Client, fragment: str) -> None:
    response = client.get(reverse('catalog:home'))

    assert fragment in response.content.decode()
