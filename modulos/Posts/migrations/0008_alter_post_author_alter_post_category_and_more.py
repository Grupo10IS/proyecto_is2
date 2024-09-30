# Generated by Django 5.1 on 2024-09-09 17:06

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import modulos.mdeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ("Categories", "0005_alter_category_description_alter_category_name_and_more"),
        ("Posts", "0007_post_image"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Autor",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="Categories.category",
                verbose_name="Categoria",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="content",
            field=modulos.mdeditor.fields.MDTextField(verbose_name="Contenido"),
        ),
        migrations.AlterField(
            model_name="post",
            name="creation_date",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Fecha de creacion"
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to="posts_images/", verbose_name="Portada"
            ),
        ),
        migrations.AlterField(
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
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="tags",
            field=models.CharField(blank=True, max_length=80, verbose_name="tags"),
        ),
        migrations.AlterField(
            model_name="post",
            name="title",
            field=models.CharField(max_length=80, verbose_name="Titulo"),
        ),
    ]
