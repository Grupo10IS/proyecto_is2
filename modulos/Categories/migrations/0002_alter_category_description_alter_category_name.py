# Generated by Django 5.1 on 2024-09-01 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Categories", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
