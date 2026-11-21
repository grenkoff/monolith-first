"""Tests of the web components of the site in a real browser."""

import os
from collections.abc import Iterator
from typing import Final

import pytest
from playwright.sync_api import Browser, Page, Playwright, expect, sync_playwright

_CORE: Final = os.environ.get('CORE_URL', 'http://localhost:8000')


@pytest.fixture(scope='module')
def playwright() -> Iterator[Playwright]:
    """Starts Playwright for the tests of the module."""
    with sync_playwright() as started:
        yield started


@pytest.fixture(scope='module')
def browser(playwright: Playwright) -> Iterator[Browser]:
    """Launches Chromium without a window."""
    launched = playwright.chromium.launch()
    yield launched
    launched.close()


@pytest.fixture
def page(browser: Browser) -> Iterator[Page]:
    """Opens a page in a fresh context, with empty storage."""
    context = browser.new_context(base_url=_CORE)
    yield context.new_page()
    context.close()


@pytest.fixture(scope='module')
def product(playwright: Playwright) -> str:
    """Puts a product on sale for 3.50 through the API and returns its id."""
    api = playwright.request.new_context(base_url=_CORE)
    answer = api.post(
        '/api/v1/catalog/products/',
        data={'name': 'Browser tea', 'price_cents': 350},
    )
    identifier = str(answer.json()['id'])
    api.dispose()
    return identifier


def test_switcher_restyles_the_page_and_remembers(page: Page) -> None:
    page.goto('/')
    page.get_by_label('Theme').select_option('bold')
    expect(page.locator('html')).to_have_attribute('data-theme', 'bold')

    page.reload()

    expect(page.locator('html')).to_have_attribute('data-theme', 'bold')


def test_total_follows_the_quantity(page: Page, product: str) -> None:
    page.goto(f'/products/{product}/')

    page.get_by_label('Quantity').fill('3')

    expect(page.locator('output[name="total"]')).to_have_text('10.50')


def test_total_is_blank_for_a_wrong_quantity(page: Page, product: str) -> None:
    page.goto(f'/products/{product}/')

    page.get_by_label('Quantity').fill('0')

    expect(page.locator('output[name="total"]')).to_have_text('—')
