from django.core.management.base import BaseCommand
from django.utils import timezone
from modulos.Posts.models import Post

class Command(BaseCommand):
    help = 'Inactiva los posts cuya fecha de validez ha expirado'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        # Buscar posts expirados que estén en estado "Publicado" y activos
        expired_posts = Post.objects.filter(
            expiration_date__lte=now,
            status=Post.PUBLISHED,
            active=True  # Solo los que están activos
        )

        for post in expired_posts:
            post.active = False  # Cambiar a inactivo
            post.save()
            self.stdout.write(self.style.SUCCESS(f"Post '{post.title}' ha sido inactivado porque ha expirado."))

        if not expired_posts.exists():
            self.stdout.write(self.style.SUCCESS("No hay posts expirados para inactivar."))
