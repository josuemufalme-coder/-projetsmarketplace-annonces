"""Routage racine de Kongo Market."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import SITEMAPS

admin.site.site_header = "Kongo Market — Administration"
admin.site.site_title = "Kongo Market"
admin.site.index_title = "Tableau de bord"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("compte/", include("comptes.urls")),
    path("", include("annonces.urls")),
    path("", include("messagerie.urls")),
    path("", include("avis.urls")),
    path("", include("moderation.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
