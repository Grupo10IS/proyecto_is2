# Generated by Django 5.1 on 2024-09-29 17:23

import django.db.models.deletion
from django.db import migrations, models


def populate_default_category(apps, schema_editor):
    # Obtén el modelo de Category y Post
    Category = apps.get_model("Categories", "Category")
    Post = apps.get_model("Posts", "Post")

    # Crea o obtén la categoría por defecto
    default_category, created = Category.objects.get_or_create(
        name="Categoría libre",
        defaults={
            "description": "Esta es una categoria totalmente libre donde encontraras acerca de cualquier topico",
            "status": "Activo",
            "tipo": "Gratis",
            "moderacion": "Libre",
        },
    )

    # Actualiza todas las instancias de Post que tienen category en null
    Post.objects.filter(category__isnull=True).update(category=default_category)


class Migration(migrations.Migration):

    dependencies = [
        ("Categories", "0008_alter_category_description"),
        ("Posts", "0008_alter_post_author_alter_post_category_and_more"),
    ]

    operations = [
        # Paso 1: Poblar los valores null en la ForeignKey 'category'
        migrations.RunPython(populate_default_category),
        # Paso 2: Cambiar el campo 'category' para que no permita valores null
        migrations.AlterField(
            model_name="post",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="Categories.category",
                verbose_name="Categoria",
                null=False,  # Aseguramos que no permita valores null
                blank=False,
            ),
        ),
    ]
