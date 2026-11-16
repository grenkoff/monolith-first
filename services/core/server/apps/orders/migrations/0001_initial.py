import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid7,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ('product', models.UUIDField()),
                ('quantity', models.PositiveSmallIntegerField()),
                ('total_cents', models.PositiveBigIntegerField()),
            ],
            options={
                'constraints': [
                    models.CheckConstraint(
                        condition=models.Q(('quantity__gte', 1)),
                        name='orders_order_quantity_positive',
                    ),
                ],
            },
        ),
    ]
