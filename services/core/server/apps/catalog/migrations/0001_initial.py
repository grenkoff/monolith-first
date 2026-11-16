import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
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
                ('name', models.CharField(max_length=100)),
                ('price_cents', models.PositiveIntegerField()),
            ],
            options={
                'constraints': [
                    models.CheckConstraint(
                        condition=models.Q(('price_cents__gte', 1)),
                        name='catalog_product_price_cents_positive',
                    ),
                ],
            },
        ),
    ]
