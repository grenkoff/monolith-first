"""Tests of the contrast between colours of the design system."""

import pytest

from scripts.design import Colour


@pytest.mark.parametrize(
    ('text', 'background', 'ratio'),
    [
        ('#000000', '#ffffff', 21),
        ('#777777', '#ffffff', 4.478089453577214),
        ('#0a0a0a', '#000000', 1.0607053967097675),
    ],
)
def test_contrast_follows_wcag(text: str, background: str, ratio: float) -> None:
    assert Colour(text).contrast(Colour(background)) == pytest.approx(ratio)
