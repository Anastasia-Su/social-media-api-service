# Generated by Django 4.2.10 on 2024-02-15 15:15

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        (
            "taggit",
            "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx",
        ),
        ("social", "0019_alter_profile_follow"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="hashtags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]
