"""Database models of orders."""

import uuid
from typing import final, override

from django.db import models


@final
class Order(models.Model):
    """Placed order of a catalog product, kept by the product id."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    product = models.UUIDField()
    quantity = models.PositiveSmallIntegerField()
    total_cents = models.PositiveBigIntegerField()

    class Meta:
        """Invariants of orders kept by the database."""

        constraints = (
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name='orders_order_quantity_positive',
            ),
        )

    @override
    def __str__(self) -> str:
        """Returns the id of the order."""
        return str(self.id)
