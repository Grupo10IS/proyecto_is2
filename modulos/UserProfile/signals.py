from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from modulos.Authorization.roles import SUBSCRIBER

User = get_user_model()


@receiver(post_save, sender=User)
def add_to_default_group(sender, instance, created, **kwargs):
    if created:
        suscriptor_group, created = Group.objects.get_or_create(name=SUBSCRIBER)
        instance.groups.add(suscriptor_group)
