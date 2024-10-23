from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path

from modulos.Authorization import urls as roles_urls
from modulos.Categories import urls as category_urls
from modulos.Pagos import urls as pagos_urls
from modulos.Posts import urls as posts_urls
from modulos.Posts.views import home_view
from modulos.Reports import urls as reports_urls
from modulos.UserProfile import urls as user_urls

urlpatterns = [
    path("", home_view, name="home"),
    path("users/", include(user_urls)),
    path("roles/", include(roles_urls)),
    path("categories/", include(category_urls)),
    path("posts/", include(posts_urls)),
    path("reports/", include(reports_urls)),
    re_path(r"mdeditor/", include("modulos.mdeditor.urls")),
    path("pagos/", include(pagos_urls)),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
