"""Tests of the serializer shared by the HTTP APIs."""

from typing import final

import msgspec
import pytest

from server.common.serializers import StrictMsgspecSerializer


@final
class _Order(msgspec.Struct, frozen=True):
    """Body with integers, alone and nested in a list."""

    quantity: int
    sizes: list[int]


def test_whole_floats_become_integers() -> None:
    parsed = StrictMsgspecSerializer.from_python(
        {'quantity': 2.0, 'sizes': [1.0, 3.0]},
        _Order,
        strict=None,
    )

    assert parsed == _Order(quantity=2, sizes=[1, 3])


@pytest.mark.parametrize('quantity', [2.5, '2', float('inf')])
def test_integers_stay_strict(quantity: object) -> None:
    with pytest.raises(msgspec.ValidationError):
        StrictMsgspecSerializer.from_python(
            {'quantity': quantity, 'sizes': []},
            _Order,
            strict=None,
        )
