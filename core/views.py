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
