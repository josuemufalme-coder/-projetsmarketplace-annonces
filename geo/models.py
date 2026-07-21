"""Référentiel géographique — SRS §3.2.

Deux niveaux : Ville puis Commune. Aucune localité n'est codée en dur :
tout est administrable depuis l'interface d'administration. Le niveau
Province pourra être ajouté au-dessus de Ville dans une version future.
"""

from django.db import models


class Ville(models.Model):
    nom = models.CharField("nom", max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    actif = models.BooleanField(
        "active",
        default=False,
        help_text="Seules les villes actives apparaissent dans les formulaires et filtres.",
    )

    class Meta:
        verbose_name = "ville"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Commune(models.Model):
    ville = models.ForeignKey(Ville, on_delete=models.PROTECT, related_name="communes")
    nom = models.CharField("nom", max_length=100)
    slug = models.SlugField()
    actif = models.BooleanField("active", default=True)

    class Meta:
        verbose_name = "commune"
        ordering = ["nom"]
        constraints = [
            models.UniqueConstraint(fields=["ville", "nom"], name="commune_nom_unique_par_ville"),
            models.UniqueConstraint(fields=["ville", "slug"], name="commune_slug_unique_par_ville"),
        ]

    def __str__(self):
        return f"{self.nom} ({self.ville.nom})"
