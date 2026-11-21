"""Amounts of money as pages show them."""

from typing import final, override

import attrs


@final
@attrs.define(slots=True, frozen=True)
class Cents:
    """Amount of money in cents, shown with two decimals."""

    _amount: int

    @override
    def __str__(self) -> str:
        """Returns the amount with two decimals, like 12.05."""
        units, cents = divmod(self._amount, 100)
        return '.'.join((str(units), str(cents).zfill(2)))
