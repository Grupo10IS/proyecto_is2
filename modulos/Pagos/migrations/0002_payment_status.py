# Generated by Django 5.1 on 2024-09-19 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pagos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(default='pending', max_length=20),
        ),
    ]
