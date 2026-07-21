"""Routage racine de Kongo Market."""

from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Kongo Market — Administration"
admin.site.site_title = "Kongo Market"
admin.site.index_title = "Tableau de bord"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("compte/", include("comptes.urls")),
    path("", include("core.urls")),
]
