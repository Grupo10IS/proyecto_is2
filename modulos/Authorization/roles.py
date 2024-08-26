# Authorization/roles.py

from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group
from django.dispatch import receiver

# Constante para el rol de admin
ADMIN = "admin"


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    groups = ["suscriptor", "autor", "editor", "publicador", "admin"]
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)
