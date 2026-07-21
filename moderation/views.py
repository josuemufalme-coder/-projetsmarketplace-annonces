from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from annonces.models import Annonce
from core.ratelimit import limiter_debit

from .antispam import evaluer_signalements
from .models import MotifSignalement, Signalement


@limiter_debit("signalement")
def signaler(request, pk):
    """Bouton « Signaler » — SRS §3.7, accessible aussi aux visiteurs."""
    annonce = get_object_or_404(Annonce, pk=pk)
    motifs = MotifSignalement.objects.filter(actif=True)
    if request.method == "POST":
        motif = motifs.filter(pk=request.POST.get("motif")).first()
        if motif:
            Signalement.objects.create(
                annonce=annonce,
                auteur=request.user if request.user.is_authenticated else None,
                motif=motif,
                commentaire=request.POST.get("commentaire", "").strip()[:2000],
            )
            evaluer_signalements(annonce)
            messages.success(
                request, _("Merci, votre signalement sera examiné par notre équipe.")
            )
            return redirect(annonce.get_absolute_url())
        messages.error(request, _("Choisissez un motif de signalement."))
    return render(request, "moderation/signaler.html", {"annonce": annonce, "motifs": motifs})
