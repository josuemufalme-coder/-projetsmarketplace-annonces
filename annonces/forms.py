"""Formulaire de publication d'annonce — SRS §3.3.

Le formulaire est construit dynamiquement selon la catégorie : les champs
spécifiques (surface, marque, kilométrage…) viennent du référentiel
ChampCategorie. Applique les décisions Q7 (photos, max 6, obligatoires
selon la catégorie), Q8 (prix facultatif / à discuter) et le mode de
contact du SRS §3.5.
"""

from django import forms
from django.conf import settings
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from geo.models import Commune

from .models import Annonce, Photo


class SelecteurFichiersMultiples(forms.ClearableFileInput):
    allow_multiple_selected = True


class ChampFichiersMultiples(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", SelecteurFichiersMultiples(attrs={"accept": "image/*"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        nettoyer = super().clean
        if isinstance(data, (list, tuple)):
            return [nettoyer(d, initial) for d in data]
        return [nettoyer(data, initial)] if data else []


class AnnonceForm(forms.ModelForm):
    telephone = forms.CharField(
        label=_("Votre numéro de téléphone"),
        max_length=20,
        required=False,
        help_text=_("Obligatoire si vous choisissez « Numéro affiché sur l'annonce »."),
    )
    photos = ChampFichiersMultiples(label=_("Photos"), required=False)

    class Meta:
        model = Annonce
        fields = ("titre", "description", "commune", "prix", "devise", "prix_a_discuter", "contact")
        widgets = {"description": forms.Textarea(attrs={"rows": 6})}

    def __init__(self, *args, categorie, utilisateur, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorie = categorie
        self.utilisateur = utilisateur
        self.fields["commune"].queryset = Commune.objects.filter(
            actif=True, ville__actif=True
        ).select_related("ville")
        if utilisateur.commune_id:
            self.fields["commune"].initial = utilisateur.commune_id
        self.fields["telephone"].initial = utilisateur.telephone
        self.fields["photos"].help_text = _("Jusqu'à %(max)s photos.") % {
            "max": settings.ANNONCE_MAX_PHOTOS
        }
        if categorie.photos_obligatoires:
            self.fields["photos"].help_text = _("Au moins une photo est requise. Jusqu'à %(max)s photos.") % {
                "max": settings.ANNONCE_MAX_PHOTOS
            }

        # Champs spécifiques de la catégorie, définis dans le référentiel.
        for champ in categorie.champs.filter(actif=True):
            libelle = champ.nom + (f" ({champ.unite})" if champ.unite else "")
            if champ.type == champ.Type.NOMBRE:
                formulaire = forms.FloatField(label=libelle, required=champ.obligatoire, min_value=0)
            elif champ.type == champ.Type.LISTE:
                formulaire = forms.ChoiceField(
                    label=libelle,
                    required=champ.obligatoire,
                    choices=[("", "---------")] + [(o, o) for o in champ.options],
                )
            else:
                formulaire = forms.CharField(label=libelle, required=champ.obligatoire, max_length=120)
            self.fields[f"champ_{champ.code}"] = formulaire

    def clean_photos(self):
        fichiers = self.files.getlist("photos")
        if len(fichiers) > settings.ANNONCE_MAX_PHOTOS:
            raise forms.ValidationError(
                _("Vous pouvez joindre au maximum %(max)s photos.") % {"max": settings.ANNONCE_MAX_PHOTOS}
            )
        return self.cleaned_data["photos"]

    def clean(self):
        donnees = super().clean()

        # Décision Q8 : soit un prix + devise, soit « à discuter ».
        if donnees.get("prix_a_discuter"):
            donnees["prix"] = None
            donnees["devise"] = ""
        elif donnees.get("prix") in (None, "") or not donnees.get("devise"):
            self.add_error(
                "prix",
                _("Indiquez un prix et sa devise, ou cochez « Prix à discuter »."),
            )

        # SRS §3.5 : le mode « numéro affiché » exige un numéro.
        if donnees.get("contact") == Annonce.Contact.TELEPHONE and not donnees.get("telephone"):
            self.add_error("telephone", _("Renseignez votre numéro ou choisissez la messagerie interne."))

        # Décision Q7 : photos obligatoires selon la catégorie.
        if self.categorie.photos_obligatoires and not self.files.getlist("photos"):
            self.add_error("photos", _("Ajoutez au moins une photo pour cette catégorie."))

        # Règle AS3 (Annexe A) : refus d'une annonce strictement identique.
        from moderation.antispam import est_doublon_strict

        if donnees.get("titre") and donnees.get("description"):
            if est_doublon_strict(self.utilisateur, donnees["titre"], donnees["description"]):
                self.add_error(
                    "titre",
                    _("Vous avez déjà une annonce identique en ligne. Renouvelez-la plutôt que de la republier."),
                )

        return donnees

    def valeurs_attributs(self):
        valeurs = {}
        for champ in self.categorie.champs.filter(actif=True):
            valeur = self.cleaned_data.get(f"champ_{champ.code}")
            if valeur not in (None, ""):
                valeurs[champ.code] = valeur
        return valeurs

    def save(self, commit=True):
        from django.utils import timezone

        annonce = super().save(commit=False)
        annonce.vendeur = self.utilisateur
        annonce.categorie = self.categorie
        annonce.attributs = self.valeurs_attributs()
        annonce.slug = slugify(annonce.titre)[:140] or "annonce"
        annonce.date_publication = timezone.now()
        if commit:
            annonce.save()
            for ordre, fichier in enumerate(self.cleaned_data["photos"], start=1):
                Photo.objects.create(annonce=annonce, image=fichier, ordre=ordre)
            telephone = self.cleaned_data.get("telephone", "").strip()
            if telephone and telephone != self.utilisateur.telephone:
                self.utilisateur.telephone = telephone
                self.utilisateur.save(update_fields=["telephone"])
            # Analyse anti-spam à la publication (décision Q2) : marque
            # pour revue humaine, ne bloque jamais ici.
            from moderation.antispam import evaluer_annonce

            evaluer_annonce(annonce)
        return annonce
