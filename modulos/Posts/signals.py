from django.core.mail import send_mail
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver

from modulos.Posts.models import Post
from modulos.UserProfile.models import UserProfile

from .models import Post, get_highlighted_post, get_popular_posts



