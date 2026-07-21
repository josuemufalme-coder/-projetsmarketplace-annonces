from django import forms
from django.contrib.auth.forms import UserCreationForm

from geo.models import Commune

from .models import Utilisateur


def _communes_actives():
    return Commune.objects.filter(actif=True, ville__actif=True).select_related("ville")


class InscriptionForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = ("email", "nom_affichage", "commune", "telephone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["commune"].queryset = _communes_actives()


class ProfilForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ("nom_affichage", "commune", "telephone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["commune"].queryset = _communes_actives()
