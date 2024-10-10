from django.db import models
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
    INACTIVE = "INACTIVE"

    STATUS_CHOICES = [
        (DRAFT, DRAFT),
        (PENDING_REVIEW, PENDING_REVIEW),
        (PENDING_PUBLICATION, PENDING_PUBLICATION),
        (PUBLISHED, PUBLISHED),
        (INACTIVE, INACTIVE),
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
    # FIX: repensar el tema de los tags
    tags = models.CharField(name="tags", max_length=80, blank=True, verbose_name="tags")
    version = models.IntegerField(default=1)

    favorites = models.ManyToManyField(
        UserProfile, related_name="favorite_posts", verbose_name="Favoritos"
    )


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


class Log(models.Model):
    creation_date = models.DateTimeField(default=now, verbose_name="Fecha de creacion")
    message = models.CharField(max_length=800, verbose_name="description")
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def creation_log(post, user):
        Log(
            post=post,
            message='El post a sido exitosamente creado por "{user.username}"',
        ).save()

    def edition_log(old_instance, new_instance, user):
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
                changes.append(
                    f'Campo {field_name} actualizado por "{user.username}".\n'
                )

        if len(changes) != 0:
            Log(post=new_instance, message="".join(changes)).save()

            # guardar un registro de las versiones del post (solo si existen cambios)
            version = NewVersion(old_instance)
            version.save()
