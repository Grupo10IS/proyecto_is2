# Generated by Django 5.1 on 2024-09-06 00:35

import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Posts", "0004_tag_post_tags"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="tags",
        ),
        migrations.AddField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="creation_date",
            field=models.DateTimeField(default=datetime.date(2024, 9, 6)),
        ),
        migrations.AddField(
            model_name="post",
            name="status",
            field=models.CharField(
                choices=[
                    ("Borrador", "Borrador"),
                    ("Rechazado", "Rechazado"),
                    ("Publicado", "Publicado"),
                ],
                default="Borrador",
                max_length=20,
            ),
        ),
        migrations.DeleteModel(
            name="Tag",
        ),
        migrations.AddField(
            model_name="post",
            name="tags",
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
