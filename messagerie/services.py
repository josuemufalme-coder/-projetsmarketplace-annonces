"""Envoi des notifications e-mail de la messagerie (décision Q5)."""

from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext as _


def notifier_nouveau_message(message):
    """Prévient le destinataire par e-mail, avec regroupement : si des
    messages du fil sont déjà non lus, il a déjà été prévenu."""
    conversation = message.conversation
    destinataire = conversation.interlocuteur(message.expediteur)
    deja_non_lus = conversation.non_lus_pour(destinataire).exclude(pk=message.pk).exists()
    if deja_non_lus or not destinataire.email:
        return
    url = f"{settings.SITE_URL}/messages/{conversation.pk}/"
    send_mail(
        subject=_("Nouveau message sur Kongo Market — %(annonce)s")
        % {"annonce": conversation.annonce.titre},
        message=_(
            "%(expediteur)s vous a écrit au sujet de l'annonce « %(annonce)s ».\n\n"
            "%(texte)s\n\n"
            "Répondez ici : %(url)s"
        )
        % {
            "expediteur": message.expediteur.nom_affichage,
            "annonce": conversation.annonce.titre,
            "texte": message.texte[:500],
            "url": url,
        },
        from_email=None,  # DEFAULT_FROM_EMAIL
        recipient_list=[destinataire.email],
        fail_silently=True,
    )
