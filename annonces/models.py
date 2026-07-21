"""Référentiel des catégories et de leurs champs spécifiques — SRS §3.3.

Chaque catégorie porte son paramètre « photos obligatoires » (décision Q7)
et ses champs spécifiques structurés (surface, kilométrage…), définis en
base : ajouter un champ à une catégorie se fait depuis l'administration,
sans migration. Le modèle Annonce lui-même arrivera à l'étape suivante.
"""

from django.db import models
from django.utils.translation import get_language


class ReferentielTraduisible(models.Model):
    """Libellé traduisible fr/ln/en ; le français sert de repli (SRS §3.9)."""

    nom_fr = models.CharField("nom (français)", max_length=100)
    nom_ln = models.CharField("nom (lingala)", max_length=100, blank=True)
    nom_en = models.CharField("nom (anglais)", max_length=100, blank=True)

    class Meta:
        abstract = True

    @property
    def nom(self):
        langue = (get_language() or "fr")[:2]
        return getattr(self, f"nom_{langue}", "") or self.nom_fr

    def __str__(self):
        return self.nom_fr


class Categorie(ReferentielTraduisible):
    slug = models.SlugField(unique=True)
    ordre = models.PositiveSmallIntegerField(default=0)
    photos_obligatoires = models.BooleanField(
        default=False,
        help_text="Au moins une photo exigée à la publication (décision Q7).",
    )
    actif = models.BooleanField("active", default=True)

    class Meta:
        verbose_name = "catégorie"
        ordering = ["ordre", "nom_fr"]


class ChampCategorie(ReferentielTraduisible):
    """Définition d'un champ spécifique d'une catégorie (« DéfinitionDeChamp » du SRS §4)."""

    class Type(models.TextChoices):
        TEXTE = "texte", "Texte"
        NOMBRE = "nombre", "Nombre"
        LISTE = "liste", "Liste de valeurs"

    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name="champs")
    code = models.SlugField(
        "code technique",
        help_text="Identifiant stable du champ, utilisé pour stocker les valeurs des annonces.",
    )
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.TEXTE)
    options = models.JSONField(
        default=list,
        blank=True,
        help_text="Valeurs proposées pour un champ de type « liste » (une par ligne).",
    )
    unite = models.CharField("unité", max_length=20, blank=True, help_text="Ex. : m², km")
    obligatoire = models.BooleanField(default=False)
    ordre = models.PositiveSmallIntegerField(default=0)
    actif = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "champ de catégorie"
        verbose_name_plural = "champs de catégorie"
        ordering = ["ordre"]
        constraints = [
            models.UniqueConstraint(fields=["categorie", "code"], name="champ_code_unique_par_categorie"),
        ]
