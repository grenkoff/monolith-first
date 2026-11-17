import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
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
                ('quantity', models.PositiveIntegerField()),
                (
                    'product',
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        related_name='sales',
                        to='catalog.product',
                    ),
                ),
            ],
        ),
    ]
