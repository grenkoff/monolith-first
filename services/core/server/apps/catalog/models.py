"""Database models of the catalog."""

import uuid
from typing import final, override

from django.db import models

from server.apps.catalog.logic.constants import NAME_MAX_LENGTH


@final
class Product(models.Model):
    """Product on sale with its price in cents."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    price_cents = models.PositiveIntegerField()

    class Meta:
        """Invariants of products kept by the database."""

        constraints = (
            models.CheckConstraint(
                condition=models.Q(price_cents__gte=1),
                name='catalog_product_price_cents_positive',
            ),
        )

    @override
    def __str__(self) -> str:
        """Returns the name of the product."""
        return self.name


@final
class Sale(models.Model):
    """Items of a product sold by one placed order, kept by its event id."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='sales',
    )
    quantity = models.PositiveIntegerField()

    @override
    def __str__(self) -> str:
        """Returns the id of the event that reported the sale."""
        return str(self.id)
