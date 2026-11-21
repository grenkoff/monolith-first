"""Tests of amounts of money shown on pages."""

import pytest

from server.common.money import Cents


@pytest.mark.parametrize(
    ('amount', 'shown'),
    [
        (0, '0.00'),
        (5, '0.05'),
        (350, '3.50'),
        (1205, '12.05'),
        (100000, '1000.00'),
    ],
)
def test_cents_are_shown_with_two_decimals(amount: int, shown: str) -> None:
    assert str(Cents(amount)) == shown
