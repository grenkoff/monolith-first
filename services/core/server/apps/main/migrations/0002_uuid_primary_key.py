import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    """Gives blog posts UUIDv7 primary keys."""

    dependencies = [('main', '0001_initial')]

    operations = [
        migrations.DeleteModel(name='BlogPost'),
        migrations.CreateModel(
            name='BlogPost',
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
                ('title', models.CharField(max_length=80)),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'BlogPost',
                'verbose_name_plural': 'BlogPosts',
            },
        ),
    ]
