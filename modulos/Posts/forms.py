from django.forms.models import ModelForm

from modulos.Posts.models import Post


# TODO: expandir
class NewPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]
