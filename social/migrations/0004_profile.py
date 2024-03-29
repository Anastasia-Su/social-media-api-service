# Generated by Django 5.0.1 on 2024-01-29 09:43

import social.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0003_alter_post_unique_together"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("bio", models.TextField()),
                (
                    "image",
                    models.ImageField(
                        null=True, upload_to=social.models.profile_picture_file_path
                    ),
                ),
                ("user", models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
