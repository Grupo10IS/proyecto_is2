# Generated by Django 5.1 on 2024-09-20 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserProfile', '0007_userprofile_receive_notifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='receive_notifications',
            field=models.BooleanField(default=False, verbose_name='Desea recibir notificaciones sobre nuevas publicaciones?'),
        ),
    ]
