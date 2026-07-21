from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Avis


class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ("note", "commentaire")
        labels = {"note": _("Votre note"), "commentaire": _("Votre commentaire")}
        widgets = {
            "note": forms.RadioSelect(choices=[(i, "★" * i) for i in range(1, 6)]),
            "commentaire": forms.Textarea(attrs={"rows": 3}),
        }
