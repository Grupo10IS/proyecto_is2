from django.db import models
from django.db.models import Count
from django.utils.timezone import now

from modulos.Categories.models import Category
from modulos.mdeditor.fields import MDTextField
from modulos.UserProfile.models import UserProfile


# Create your models here.
class Post(models.Model):
    DRAFT = "Borrador"
    PENDING_REVIEW = "Esperando revision"
    PENDING_PUBLICATION = "Esperando publicacion"
    PUBLISHED = "Publicado"

    STATUS_CHOICES = [
        (DRAFT, DRAFT),
        (PENDING_REVIEW, PENDING_REVIEW),
        (PENDING_PUBLICATION, PENDING_PUBLICATION),
        (PUBLISHED, PUBLISHED),
    ]

    title = models.CharField(max_length=80, verbose_name="Titulo")
    image = models.ImageField(
        upload_to="posts_images/", verbose_name="Portada", blank=True, null=True
    )
    content = MDTextField(name="content", verbose_name="Contenido")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=False, verbose_name="Categoria"
    )
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default=DRAFT, verbose_name="Status"
    )
    active = models.BooleanField(default=True)
    creation_date = models.DateTimeField(default=now, verbose_name="Fecha de creacion")
    publication_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de publicacion"
    )
    scheduled_publication_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de publicacion agendada"
    )
    expiration_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de validez"
    )
    author = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, verbose_name="Autor"
    )
    tags = models.CharField(name="tags", max_length=80, blank=True, verbose_name="tags")
    version = models.IntegerField(default=1)

    favorites = models.ManyToManyField(
        UserProfile, related_name="favorite_posts", verbose_name="Favoritos"
    )


def get_popular_posts():
    """
    Obtiene los 5 posts más populares. Los posts mas populares son aquellos con
    mas conteo de favoritos.
    """
    # Obtener los 5 posts más populares (mayor conteo de favoritos)
    posts_populares = (
        Post.objects.filter(status=Post.PUBLISHED, active=True)
        .annotate(favorite_count=Count("favorites"))
        .order_by("-favorite_count")[:5]
    )

    return posts_populares


class Version(models.Model):
    post_id = models.IntegerField(null=False)
    title = models.CharField(max_length=80, verbose_name="Titulo")
    image = models.ImageField(
        upload_to="posts_images/", verbose_name="Portada", blank=True, null=True
    )
    content = MDTextField(name="content", verbose_name="Contenido", null=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, verbose_name="Categoria"
    )
    status = models.CharField(max_length=30, verbose_name="Status")
    creation_date = models.DateTimeField(default=now, verbose_name="Fecha de creacion")
    publication_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de publicacion"
    )
    scheduled_publication_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de publicacion agendada"
    )
    author = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, verbose_name="Autor"
    )
    tags = models.CharField(name="tags", max_length=80, blank=True, verbose_name="tags")

    version = models.IntegerField(default=0)


def NewVersion(post: Post) -> Version:
    return Version(
        title=post.title,
        image=post.image,
        content=post.content,
        category=post.category,
        status=post.status,
        publication_date=post.publication_date,
        scheduled_publication_date=post.scheduled_publication_date,
        author=post.author,
        tags=post.tags,
        version=post.version,
        post_id=post.id,
    )


def RestorePost(post: Post, version: Version) -> None:
    """
    Esta funcion restaura un post a una version especificada.

    El post actualizara a su version (+1) y copiara la informacion de la version
    especificada para la regresion
    """
    NewVersion(post).save()

    post.title = version.title
    post.image = version.image
    post.content = version.content
    post.category = version.category
    post.status = version.status
    post.publication_date = version.publication_date
    post.scheduled_publication_date = version.scheduled_publication_date
    post.author = version.author
    post.tags = version.tags
    post.version += 1

    post.save()


class Log(models.Model):
    """
    Clase que representa los logs de un post especifico.

    NO se debe instanciar de forma manual, para ello se proporcionan las funciones:
        - new_creation_log
        - new_edition_log
    """

    creation_date = models.DateTimeField(default=now, verbose_name="Fecha de creacion")
    message = models.CharField(max_length=800, verbose_name="description")
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


def new_creation_log(post, user) -> None:
    """
    Metodo para generar un nuevo log cuando se realiza la creacion de un nuevo post.

    Dentro de los mensajes se especificara el nombre de usuario del autor.
    """
    Log(
        post=post,
        message=f'El post a sido exitosamente creado por "{user.username}"',
    ).save()


def new_edition_log(old_instance, new_instance, user) -> None:
    """
    Metodo para generar un nuevo log cuando se realiza una edicion de un campo sobre un post.

    Todas los cambios sobre el contenido seran reporatadas y generaran un nuevo log el
    cual contendra la fecha de la accion, la accion en si, el campo donde se realizo la actualizacion
    y el usuario que la realizo.

    Dentro de los mensajes se especificara el nombre de usuario el cual realizo dicho cmabio.
    """
    changes = []
    for field in old_instance._meta.fields:
        field_name = field.name
        old_value = getattr(old_instance, field_name)
        new_value = getattr(new_instance, field_name)

        if old_value != new_value:
            changes.append(f'Campo {field_name} actualizado por "{user.username}".\n')

    if len(changes) != 0:
        Log(post=new_instance, message="".join(changes)).save()

        # guardar un registro de las versiones del post (solo si existen cambios)
        version = NewVersion(old_instance)
        version.save()


def is_valid(self):
    """Devuelve True si el post es válido para ser mostrado"""
    if self.expiration_date:
        return self.publication_date <= now() <= self.expiration_date
    return self.publication_date


# Lista con los posts destacados manualmente por el admin.
class Destacado(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(default=now, verbose_name="Fecha de destacado")


def get_highlighted_post():
    """
    Retorna el post destacado del momento. El post destacado es el ultimo en ser anadido
    a la lista.
    """
    # Obtener el post destacado (destacado por el admin)
    # post_destacado = (
    #     Destacado.objects.filter(post__status=Post.PUBLISHED, post__active=True)
    #     .order_by("-date")
    #     .first()
    # )

    # if post_destacado == None:
        # return None

    # return post_destacado.post
    return None
