"""Messagerie interne — SRS §3.5, décision Q5.

Un fil de conversation par couple acheteur / annonce. Le destinataire
d'un nouveau message est prévenu par e-mail, avec regroupement : pas de
nouvel e-mail tant qu'il n'a pas lu les messages précédents du fil.
"""

from django.db import models


class Conversation(models.Model):
    annonce = models.ForeignKey(
        "annonces.Annonce", on_delete=models.CASCADE, related_name="conversations"
    )
    acheteur = models.ForeignKey(
        "comptes.Utilisateur", on_delete=models.CASCADE, related_name="conversations_achat"
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "conversation"
        constraints = [
            models.UniqueConstraint(fields=["annonce", "acheteur"], name="un_fil_par_acheteur_et_annonce"),
        ]

    def __str__(self):
        return f"{self.acheteur} ↔ {self.annonce}"

    @property
    def vendeur(self):
        return self.annonce.vendeur

    def interlocuteur(self, utilisateur):
        return self.vendeur if utilisateur == self.acheteur else self.acheteur

    def non_lus_pour(self, utilisateur):
        return self.messages.exclude(expediteur=utilisateur).filter(lu=False)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    expediteur = models.ForeignKey(
        "comptes.Utilisateur", on_delete=models.CASCADE, related_name="messages_envoyes"
    )
    texte = models.TextField("message")
    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    class Meta:
        verbose_name = "message"
        ordering = ["date"]
