"""Tests of the similarity computed by the Rust extension module."""

import pytest

from server.apps.catalog.infra.ranking import RustSimilarity


def test_rust_scores_each_name_in_order() -> None:
    scores = RustSimilarity().scores('tee', ['Green tea', 'Black coffee'])

    assert scores == pytest.approx([2 / 3, 1 / 3])


def test_rust_scores_no_names() -> None:
    assert RustSimilarity().scores('tea', []) == []
