from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from comptes.models import Utilisateur

from .forms import AvisForm
from .models import Avis, peut_laisser_avis


@login_required
@require_POST
def laisser_avis(request, pk):
    vendeur = get_object_or_404(Utilisateur, pk=pk, is_active=True)
    if not peut_laisser_avis(request.user, vendeur):
        messages.error(
            request,
            _("Vous devez d'abord contacter ce vendeur (numéro ou message) pour laisser un avis."),
        )
        return redirect("comptes:vendeur", pk=vendeur.pk)
    existant = Avis.objects.filter(auteur=request.user, vendeur=vendeur).first()
    form = AvisForm(request.POST, instance=existant)
    if form.is_valid():
        avis = form.save(commit=False)
        avis.auteur = request.user
        avis.vendeur = vendeur
        avis.save()
        messages.success(request, _("Merci pour votre avis !"))
    else:
        messages.error(request, _("Choisissez une note de 1 à 5 étoiles."))
    return redirect("comptes:vendeur", pk=vendeur.pk)
