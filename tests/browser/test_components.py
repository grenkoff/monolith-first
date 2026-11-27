"""Tests of the web components of the site in a real browser."""

import os
from collections.abc import Iterator
from typing import Final

import pytest
from playwright.sync_api import Browser, Page, Playwright, expect, sync_playwright

_CORE: Final = os.environ.get('CORE_URL', 'http://localhost:8000')
_STAFF: Final = os.environ.get('STAFF', 'browser-staff')


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


@pytest.fixture
def staff(page: Page) -> Iterator[Page]:
    """Signs staff in and puts back the theme of the site they found."""
    page.goto('/admin/login/?next=/')
    page.get_by_label('Username').fill(_STAFF)
    page.get_by_label('Password').fill(_STAFF)
    page.get_by_role('button', name='Log in').click()
    found = page.locator('html').get_attribute('data-theme') or 'classic'
    yield page
    page.goto('/')
    page.get_by_label('Theme').select_option(found)
    expect(page.locator('html')).to_have_attribute('data-theme', found)


def test_staff_choice_restyles_the_site_at_once(staff: Page) -> None:
    staff.goto('/')

    staff.get_by_label('Theme').select_option('bold')

    expect(staff.locator('html')).to_have_attribute('data-theme', 'bold')


def test_visitors_see_the_theme_staff_chose(staff: Page, browser: Browser) -> None:
    staff.goto('/')
    staff.get_by_label('Theme').select_option('warm')
    expect(staff.locator('html')).to_have_attribute('data-theme', 'warm')
    visitor = browser.new_context(base_url=_CORE)

    page = visitor.new_page()
    page.goto('/')

    expect(page.locator('html')).to_have_attribute('data-theme', 'warm')
    visitor.close()


def test_total_follows_the_quantity(page: Page, product: str) -> None:
    page.goto(f'/products/{product}/')

    page.get_by_label('Quantity').fill('3')

    expect(page.locator('output[name="total"]')).to_have_text('10.50')


def test_total_is_blank_for_a_wrong_quantity(page: Page, product: str) -> None:
    page.goto(f'/products/{product}/')

    page.get_by_label('Quantity').fill('0')

    expect(page.locator('output[name="total"]')).to_have_text('—')
