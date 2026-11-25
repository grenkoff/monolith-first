"""Tests of the health endpoint of the HTTP API."""

from http import HTTPStatus
from typing import Final

from django.test import Client
from django.urls import reverse
from dmr.test import DMRClient
from pytest_django import DjangoAssertNumQueries

_HEALTH: Final = '/api/v1/health/'


def test_health_answers_ok(dmr_client: DMRClient) -> None:
    response = dmr_client.get(_HEALTH)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'status': 'ok'}


def test_health_makes_no_database_query(
    dmr_client: DMRClient,
    django_assert_num_queries: DjangoAssertNumQueries,
    db: None,
) -> None:
    with django_assert_num_queries(0):
        response = dmr_client.get(_HEALTH)

    assert response.status_code == HTTPStatus.OK


def test_health_is_in_the_openapi_schema(admin_client: Client) -> None:
    schema = admin_client.get(reverse('v1_openapi_json')).json()

    assert 'get' in schema['paths'].get(_HEALTH, {})
