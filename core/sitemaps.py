"""Plan du site pour les moteurs de recherche — annonces actives et pages clés."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from annonces.models import Annonce


class AnnoncesSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Annonce.objects.actives().select_related("categorie", "commune")

    def lastmod(self, annonce):
        return annonce.date_publication


class PagesSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.9

    def items(self):
        return ["core:home", "annonces:liste"]

    def location(self, nom):
        return reverse(nom)


SITEMAPS = {"annonces": AnnoncesSitemap, "pages": PagesSitemap}
