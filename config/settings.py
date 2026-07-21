"""
Réglages Django de Kongo Market.

Toute valeur dépendante de l'environnement (production Railway vs poste
local) est lue depuis les variables d'environnement, avec des valeurs par
défaut adaptées au développement local. En production, définir au minimum :
DJANGO_SECRET_KEY, DJANGO_DEBUG=false, DJANGO_ALLOWED_HOSTS,
DATABASE_URL (fournie par Railway).
"""

import os
from pathlib import Path

import dj_database_url
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-insecure-key-remplacer-en-production",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "geo",
    "annonces",
    "comptes",
]

AUTH_USER_MODEL = "comptes.Utilisateur"
LOGIN_URL = "comptes:connexion"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Base de données : PostgreSQL en production via DATABASE_URL (Railway),
# SQLite en local pour démarrer sans installation.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalisation — SRS §3.9 : français (défaut), lingala, anglais.
LANGUAGE_CODE = "fr"

LANGUAGES = [
    ("fr", _("Français")),
    ("ln", _("Lingala")),
    ("en", _("Anglais")),
]

# Le lingala n'est pas dans le registre de langues fourni par Django :
# on l'y déclare pour que LocaleMiddleware et le sélecteur l'acceptent.
from django.conf.locale import LANG_INFO  # noqa: E402

LANG_INFO.setdefault(
    "ln",
    {
        "bidi": False,
        "code": "ln",
        "name": "Lingala",
        "name_local": "Lingála",
    },
)

LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "Africa/Kinshasa"
USE_I18N = True
USE_TZ = True

# Fichiers statiques servis par WhiteNoise (compressés + empreinte de cache).
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Le stockage avec manifeste exige un collectstatic préalable : on ne
# l'active qu'en vraie production (ni debug, ni tests).
import sys  # noqa: E402

_EN_TEST = "test" in sys.argv
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if not DEBUG and not _EN_TEST
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        )
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Derrière le proxy Railway/Cloudflare, la requête d'origine est en HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
