# Generated by Django 5.1 on 2024-09-09 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Categories", "0004_category_status_category_tipo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Descricion"),
        ),
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=80, verbose_name="Nombre"),
        ),
        migrations.AlterField(
            model_name="category",
            name="status",
            field=models.CharField(
                choices=[("Activo", "Activo"), ("Inactivo", "Inactivo")],
                default="Activo",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="tipo",
            field=models.CharField(
                choices=[("Premium", "Premium"), ("Gratis", "Gratis")],
                default="Gratis",
                max_length=10,
            ),
        ),
    ]