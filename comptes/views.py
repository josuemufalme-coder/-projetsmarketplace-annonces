from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from .forms import InscriptionForm, ProfilForm


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
