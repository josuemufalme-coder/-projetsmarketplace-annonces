"""Signalement et modération — SRS §3.7, décision Q2, Annexe A.

Trois sources alimentent la file de revue humaine : les signalements des
utilisateurs (bouton « Signaler », ouvert aux visiteurs), les marques
posées par les règles anti-spam, et l'initiative de l'administrateur.
Les règles automatiques ne suppriment jamais rien (sauf AS8 : masquage
temporaire réversible après 5 signalements distincts).
"""

from django.db import models

from annonces.models import ReferentielTraduisible


class MotifSignalement(ReferentielTraduisible):
    """Motifs proposés au signalement — référentiel administrable (SRS §3.7)."""

    code = models.SlugField(unique=True)
    ordre = models.PositiveSmallIntegerField(default=0)
    actif = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "motif de signalement"
        verbose_name_plural = "motifs de signalement"
        ordering = ["ordre"]


class Signalement(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        REJETE = "rejete", "Rejeté"
        TRAITE = "traite", "Traité"

    annonce = models.ForeignKey(
        "annonces.Annonce", on_delete=models.CASCADE, related_name="signalements"
    )
    auteur = models.ForeignKey(
        "comptes.Utilisateur",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="signalements",
        help_text="Vide pour un visiteur non connecté.",
    )
    motif = models.ForeignKey(MotifSignalement, on_delete=models.PROTECT)
    commentaire = models.TextField("commentaire", blank=True)
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.EN_ATTENTE)

    class Meta:
        verbose_name = "signalement"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.annonce} — {self.motif}"


class MotifFrauduleux(models.Model):
    """Liste administrable des motifs d'arnaque connus (règle AS5, Annexe A).
    Démarre vide et s'enrichit avec les arnaques réellement observées."""

    expression = models.CharField("expression à détecter", max_length=120, unique=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "motif frauduleux (anti-spam)"
        verbose_name_plural = "motifs frauduleux (anti-spam)"

    def __str__(self):
        return self.expression


class MarqueAntiSpam(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente"
        REJETEE = "rejetee", "Rejetée (fausse alerte)"
        TRAITEE = "traitee", "Traitée"

    annonce = models.ForeignKey(
        "annonces.Annonce", on_delete=models.CASCADE, related_name="marques_antispam"
    )
    regle = models.CharField("règle déclenchée", max_length=5)  # AS1…AS8
    detail = models.CharField("détail", max_length=200, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.EN_ATTENTE)

    class Meta:
        verbose_name = "marque anti-spam"
        verbose_name_plural = "marques anti-spam"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.regle} — {self.annonce}"
