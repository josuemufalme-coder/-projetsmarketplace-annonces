from django.shortcuts import render

from annonces.models import Annonce, Categorie


def home(request):
    """Accueil — SRS §3.4 : recherche, accès par catégorie, annonces récentes."""
    recentes = (
        Annonce.objects.actives()
        .select_related("categorie", "commune")
        .prefetch_related("photos")[:8]
    )
    return render(
        request,
        "core/home.html",
        {"categories": Categorie.objects.filter(actif=True), "recentes": recentes},
    )


def robots(request):
    """robots.txt : indexer le contenu public, pas les espaces privés."""
    from django.http import HttpResponse

    lignes = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /compte/",
        "Disallow: /messages/",
        "Disallow: /publier/",
        "Disallow: /mes-annonces/",
        "Disallow: /signaler/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        "",
    ]
    return HttpResponse("\n".join(lignes), content_type="text/plain")
