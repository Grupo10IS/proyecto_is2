# Generated by Django 5.1 on 2024-09-03 17:41

from django.db import migrations

import modulos.mdeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ("Posts", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="category",
        ),
        migrations.RemoveField(
            model_name="post",
            name="status",
        ),
        migrations.AlterField(
            model_name="post",
            name="content",
            field=modulos.mdeditor.fields.MDTextField(),
        ),
    ]
