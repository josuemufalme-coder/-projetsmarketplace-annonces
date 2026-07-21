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
    "django.contrib.sitemaps",
    "core",
    "geo",
    "annonces",
    "comptes",
    "messagerie",
    "avis",
    "moderation",
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
                "messagerie.context_processors.messages_non_lus",
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

# Fichiers envoyés par les utilisateurs (photos d'annonces).
# En local : disque. En production : stockage objet S3/R2 (étape déploiement).
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Paramètres métier des annonces (SRS §3.3, décisions Q7 et Q10) —
# configurables sans redéploiement via variables d'environnement.
ANNONCE_DUREE_JOURS = int(os.environ.get("ANNONCE_DUREE_JOURS", 30))
ANNONCE_RENOUVELLEMENT_JOURS = int(os.environ.get("ANNONCE_RENOUVELLEMENT_JOURS", 7))
ANNONCE_MAX_PHOTOS = int(os.environ.get("ANNONCE_MAX_PHOTOS", 6))

# Limitation de débit (SRS §5.3) — format « nombre/secondes ».
def _limite_debit(nom, defaut):
    brut = os.environ.get(f"RATELIMIT_{nom}", defaut)
    nombre, fenetre = brut.split("/")
    return (int(nombre), int(fenetre))


RATE_LIMITS = {
    "inscription": _limite_debit("INSCRIPTION", "5/3600"),      # 5 comptes/h par IP
    "connexion": _limite_debit("CONNEXION", "10/900"),          # 10 essais/15 min
    "mdp_oublie": _limite_debit("MDP_OUBLIE", "5/3600"),        # 5 demandes/h
    "publication": _limite_debit("PUBLICATION", "15/86400"),    # 15 annonces/24 h (Annexe A, AS1)
    "message": _limite_debit("MESSAGE", "60/3600"),             # 60 messages/h
    "numero": _limite_debit("NUMERO", "30/3600"),               # 30 clics « numéro »/h
    "signalement": _limite_debit("SIGNALEMENT", "10/3600"),     # 10 signalements/h
    "avis": _limite_debit("AVIS", "10/86400"),                  # 10 avis/24 h
}

# Seuils des règles anti-spam (Annexe A du cahier des charges).
ANTISPAM_RAFALE_24H = int(os.environ.get("ANTISPAM_RAFALE_24H", 5))
ANTISPAM_NOUVEAU_COMPTE_MAX = int(os.environ.get("ANTISPAM_NOUVEAU_COMPTE_MAX", 3))
ANTISPAM_MAX_LIENS_DESCRIPTION = int(os.environ.get("ANTISPAM_MAX_LIENS_DESCRIPTION", 2))
ANTISPAM_SEUIL_SIGNALEMENTS = int(os.environ.get("ANTISPAM_SEUIL_SIGNALEMENTS", 5))
# Planchers de prix par catégorie (règle AS7), en USD.
import json as _json

ANTISPAM_PRIX_PLANCHERS_USD = _json.loads(
    os.environ.get("ANTISPAM_PRIX_PLANCHERS_USD", '{"vehicules": 100, "immobilier": 20}')
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# E-mails transactionnels (notifications de messagerie — décision Q5).
# En local : affichage console. En production : SMTP (Brevo) via variables.
EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"
DEFAULT_FROM_EMAIL = os.environ.get(
    "DJANGO_DEFAULT_FROM_EMAIL", "Kongo Market <no-reply@localhost>"
)
# Adresse publique du site, utilisée dans les liens des e-mails.
SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:8000").rstrip("/")

# Derrière le proxy Railway/Cloudflare, la requête d'origine est en HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
