"""Avis et notation des vendeurs — SRS §3.6, décision Q1.

Un avis (note 1 à 5 + commentaire) ne peut être laissé que par un
utilisateur connecté ayant une action de contact traçable envers le
vendeur : clic « Afficher le numéro » ou message interne. Un seul avis
par couple acheteur/vendeur, modifiable.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Avis(models.Model):
    auteur = models.ForeignKey(
        "comptes.Utilisateur", on_delete=models.CASCADE, related_name="avis_donnes"
    )
    vendeur = models.ForeignKey(
        "comptes.Utilisateur", on_delete=models.CASCADE, related_name="avis_recus"
    )
    note = models.PositiveSmallIntegerField(
        "note", validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    commentaire = models.TextField("commentaire", blank=True)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "avis"
        verbose_name_plural = "avis"
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["auteur", "vendeur"], name="un_avis_par_auteur_et_vendeur"),
        ]

    def __str__(self):
        return f"{self.auteur} → {self.vendeur} : {self.note}/5"


def peut_laisser_avis(auteur, vendeur):
    """Décision Q1 : contact tracé sur la plateforme requis (clic numéro ou message)."""
    if not auteur.is_authenticated or auteur == vendeur:
        return False
    from annonces.models import ClicAffichageNumero
    from messagerie.models import Message

    a_clique = ClicAffichageNumero.objects.filter(
        utilisateur=auteur, annonce__vendeur=vendeur
    ).exists()
    a_ecrit = Message.objects.filter(
        expediteur=auteur, conversation__annonce__vendeur=vendeur
    ).exists()
    return a_clique or a_ecrit
