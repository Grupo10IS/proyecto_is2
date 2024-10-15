# Generated by Django 5.1 on 2024-10-08 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Categories", "0008_alter_category_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="moderacion",
            field=models.CharField(
                choices=[("Moderada", "Moderada"), ("Libre", "Libre")],
                default="Moderada",
                max_length=15,
            ),
        ),
    ]