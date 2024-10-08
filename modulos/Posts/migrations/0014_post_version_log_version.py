# Generated by Django 5.1 on 2024-09-30 03:50

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import modulos.mdeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ("Categories", "0008_alter_category_description"),
        ("Posts", "0013_post_favorites"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="version",
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name="Log",
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
                (
                    "creation_date",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Fecha de creacion",
                    ),
                ),
                (
                    "message",
                    models.CharField(max_length=800, verbose_name="description"),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="Posts.post"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Version",
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
                ("post_id", models.IntegerField()),
                ("title", models.CharField(max_length=80, verbose_name="Titulo")),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="posts_images/",
                        verbose_name="Portada",
                    ),
                ),
                (
                    "content",
                    modulos.mdeditor.fields.MDTextField(
                        null=True, verbose_name="Contenido"
                    ),
                ),
                ("status", models.CharField(max_length=30, verbose_name="Status")),
                (
                    "creation_date",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Fecha de creacion",
                    ),
                ),
                (
                    "publication_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Fecha de publicacion"
                    ),
                ),
                (
                    "scheduled_publication_date",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Fecha de publicacion agendada",
                    ),
                ),
                (
                    "tags",
                    models.CharField(blank=True, max_length=80, verbose_name="tags"),
                ),
                ("version", models.IntegerField(default=0)),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Autor",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="Categories.category",
                        verbose_name="Categoria",
                    ),
                ),
            ],
        ),
    ]
