import os
from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-6dl*^m=jx0di(gtk0u03!of_wioc#5+l_f@&*@1xa886g2)8)r"

ALLOWED_HOSTS = ["*"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "modulos"),
]
COMPRESS_ENABLED = True
COMPRESS_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]


# Application definition
INSTALLED_APPS = [
    "compressor",
    "modulos.mdeditor.apps.MdeditorConfig",
    "modulos.UserProfile.apps.UserprofileConfig",
    "modulos.Posts.apps.PostsConfig",
    "modulos.Authorization.apps.AuthorizationConfig",
    "modulos.Categories.apps.CategoriesConfig",
    "modulos.Pagos.apps.PagosConfig",
    "modulos.Reports.apps.ReportsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_bootstrap5",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# NOTE: si vamos a cambiar deberiamos repensar la gh_action
if os.environ.get("GH_ACTION") == "True":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "proyecto",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Asuncion"
USE_I18N = True
USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "UserProfile.UserProfile"
LOGIN_REDIRECT_URL = "/user/profile/"
LOGIN_URL = "/users/login"
LOGOUT_REDIRECT_URL = "home"  # Redirigir a la página de inicio después del logout

# mdeditor
MEDIA_ROOT = os.path.join(BASE_DIR, "uploads")
MEDIA_URL = "/media/"
X_FRAME_OPTIONS = "SAMEORIGIN"

# Bootstrap library
CRISPY_TEMPLATE_PACK = "bootstrap5"

# SendGrid (correo electronico)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.sendgrid.net")
EMAIL_PORT = config("EMAIL_PORT", default=587)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config(
    "EMAIL_HOST_USER", default="apikey"
)  # Debe ser literalmente 'apikey'
EMAIL_HOST_PASSWORD = config(
    "EMAIL_HOST_PASSWORD", default="default"
)  # Tu API Key de SendGrid
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="groupmakex@gmail.com")

# stripe (pagos)
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="stripe")
STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY", default="stripe")

# Disqus (comentarios)
DISQUS_API_KEY = config("DISQUS_API_KEY", default="disqus_api")
DISQUS_FORUM = config("DISQUS_FORUM", default="makexfp-com")
