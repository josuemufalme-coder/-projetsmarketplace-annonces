from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from core.ratelimit import limiter_debit

from .forms import InscriptionForm, ProfilForm


@limiter_debit("inscription")
def inscription(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    form = InscriptionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        utilisateur = form.save()
        login(request, utilisateur)
        messages.success(request, _("Bienvenue sur Kongo Market !"))
        return redirect("core:home")
    return render(request, "comptes/inscription.html", {"form": form})


@login_required
def profil(request):
    form = ProfilForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Profil mis à jour."))
        return redirect("comptes:profil")
    return render(request, "comptes/profil.html", {"form": form})


def vendeur(request, pk):
    """Profil public d'un vendeur — SRS §3.6 : annonces actives, note, avis."""
    from django.db.models import Avg, Count
    from django.shortcuts import get_object_or_404

    from annonces.models import Annonce
    from avis.forms import AvisForm
    from avis.models import Avis, peut_laisser_avis

    from .models import Utilisateur

    profil = get_object_or_404(Utilisateur, pk=pk, is_active=True)
    statistiques = profil.avis_recus.aggregate(moyenne=Avg("note"), total=Count("id"))
    annonces = (
        Annonce.objects.actives()
        .filter(vendeur=profil)
        .select_related("categorie", "commune")
        .prefetch_related("photos")
    )
    mon_avis = None
    if request.user.is_authenticated:
        mon_avis = Avis.objects.filter(auteur=request.user, vendeur=profil).first()
    return render(
        request,
        "comptes/vendeur.html",
        {
            "profil": profil,
            "statistiques": statistiques,
            "annonces": annonces,
            "liste_avis": profil.avis_recus.select_related("auteur")[:30],
            "avis_autorise": peut_laisser_avis(request.user, profil),
            "avis_form": AvisForm(instance=mon_avis),
            "mon_avis": mon_avis,
        },
    )
