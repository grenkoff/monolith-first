"""Tests of the use case that searches products by name."""

from collections.abc import Sequence
from typing import final
from uuid import UUID, uuid7

import attrs

from server.apps.catalog.logic.usecases.search_products import SearchProducts
from server.apps.catalog.logic.value_objects import ProductDraft
from server.apps.catalog.public.products import Product, UnknownProductError


def _product(name: str) -> Product:
    """Returns a product on sale with the name."""
    return Product(id=uuid7(), name=name, price_cents=100, sold=0)


@final
@attrs.define(slots=True, frozen=True)
class _Shelf:
    """Fake: products on sale kept in a list."""

    _products: list[Product]

    def add(self, draft: ProductDraft) -> Product:
        """Puts nothing on the shelf, the tests only read it."""
        return _product(draft.name)

    def product(self, identifier: UUID) -> Product:
        """Finds nothing by id, the tests only list the shelf."""
        raise UnknownProductError(str(identifier))

    def on_sale(self) -> list[Product]:
        """Returns the products of the shelf."""
        return self._products


@final
@attrs.define(slots=True, frozen=True)
class _Scores:
    """Fake: resemblance of each name, written down by the test."""

    _scores: dict[str, float]

    def scores(self, query: str, names: Sequence[str]) -> list[float]:
        """Returns the written score of each name."""
        return [self._scores[name] for name in names]


_TEA = _product('Green tea')
_COFFEE = _product('Black coffee')
_JUICE = _product('Orange juice')
_SEARCH = SearchProducts(
    _Shelf([_COFFEE, _JUICE, _TEA]),
    _Scores({'Green tea': 0.9, 'Black coffee': 0.5, 'Orange juice': 0.49}),
)


def test_search_ranks_the_closest_names_first() -> None:
    assert _SEARCH('tea') == [_TEA, _COFFEE]


def test_search_leaves_out_distant_names() -> None:
    assert _JUICE not in _SEARCH('tea')


def test_blank_query_finds_nothing() -> None:
    assert _SEARCH('   ') == []
