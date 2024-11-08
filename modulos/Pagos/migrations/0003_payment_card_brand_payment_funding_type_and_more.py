# Generated by Django 5.1 on 2024-11-01 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pagos', '0002_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='card_brand',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='funding_type',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='last4',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(choices=[('credit_card', 'Tarjeta de Crédito'), ('debit_card', 'Tarjeta de Débito')], default='credit_card', max_length=20),
        ),
    ]