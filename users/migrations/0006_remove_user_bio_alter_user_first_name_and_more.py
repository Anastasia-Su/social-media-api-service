# Generated by Django 5.0.1 on 2024-01-29 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_alter_user_first_name_alter_user_last_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="bio",
        ),
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="first name"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="last name"
            ),
        ),
    ]