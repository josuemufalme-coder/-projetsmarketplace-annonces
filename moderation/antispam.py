"""Règles anti-spam v1 — Annexe A du cahier des charges.

Chaque règle MARQUE l'annonce pour revue humaine ; aucune ne supprime.
Seule AS8 masque temporairement (réversible) après 5 signalements de
comptes distincts. Tous les seuils sont configurables (settings).
"""

import datetime
import re

from django.conf import settings
from django.utils import timezone


def _marquer(annonce, regle, detail=""):
    from .models import MarqueAntiSpam

    MarqueAntiSpam.objects.get_or_create(
        annonce=annonce, regle=regle, defaults={"detail": detail[:200]}
    )


def est_doublon_strict(vendeur, titre, description, annonce_exclue=None):
    """AS3 (volet blocage) : refuse une annonce strictement identique à
    une annonce active du même compte."""
    from annonces.models import Annonce

    doublons = Annonce.objects.actives().filter(
        vendeur=vendeur, titre=titre.strip(), description=description.strip()
    )
    if annonce_exclue:
        doublons = doublons.exclude(pk=annonce_exclue.pk)
    return doublons.exists()


def evaluer_annonce(annonce):
    """Exécute les règles AS1–AS7 sur une annonce fraîchement publiée."""
    from annonces.models import Annonce

    from .models import MotifFrauduleux

    vendeur = annonce.vendeur
    maintenant = timezone.now()

    # AS1 — publication en rafale.
    recentes = Annonce.objects.filter(
        vendeur=vendeur, date_creation__gte=maintenant - datetime.timedelta(hours=24)
    ).count()
    if recentes > settings.ANTISPAM_RAFALE_24H:
        _marquer(annonce, "AS1", f"{recentes} annonces en 24 h")

    # AS2 — compte tout neuf très actif.
    age_compte = maintenant - vendeur.date_joined
    if age_compte < datetime.timedelta(hours=24) and recentes > settings.ANTISPAM_NOUVEAU_COMPTE_MAX:
        _marquer(annonce, "AS2", f"compte de {age_compte.total_seconds() // 3600:.0f} h")

    # AS3 — quasi-doublon du même compte (même titre, description différente).
    if (
        Annonce.objects.actives()
        .filter(vendeur=vendeur, titre__iexact=annonce.titre.strip())
        .exclude(pk=annonce.pk)
        .exists()
    ):
        _marquer(annonce, "AS3", "titre identique à une autre annonce du compte")

    # AS4 — même numéro affiché sur des comptes différents.
    if annonce.contact == Annonce.Contact.TELEPHONE and vendeur.telephone:
        if (
            Annonce.objects.actives()
            .filter(vendeur__telephone=vendeur.telephone, contact=Annonce.Contact.TELEPHONE)
            .exclude(vendeur=vendeur)
            .exists()
        ):
            _marquer(annonce, "AS4", f"numéro {vendeur.telephone} partagé")

    # AS5 — motifs frauduleux connus (liste administrable).
    texte = f"{annonce.titre} {annonce.description}".lower()
    for motif in MotifFrauduleux.objects.filter(actif=True):
        if motif.expression.lower() in texte:
            _marquer(annonce, "AS5", f"motif « {motif.expression} »")
            break

    # AS6 — liens externes.
    liens = re.findall(r"https?://|www\.", annonce.description, flags=re.IGNORECASE)
    if re.search(r"https?://|www\.", annonce.titre, flags=re.IGNORECASE):
        _marquer(annonce, "AS6", "lien dans le titre")
    elif len(liens) > settings.ANTISPAM_MAX_LIENS_DESCRIPTION:
        _marquer(annonce, "AS6", f"{len(liens)} liens dans la description")

    # AS7 — prix aberrant (plancher par catégorie, en USD).
    plancher = settings.ANTISPAM_PRIX_PLANCHERS_USD.get(annonce.categorie.slug)
    if plancher and annonce.devise == "USD" and annonce.prix is not None and annonce.prix < plancher:
        _marquer(annonce, "AS7", f"prix {annonce.prix} $ sous le plancher {plancher} $")


def evaluer_signalements(annonce):
    """AS8 — masquage temporaire (réversible) après N signalements de
    comptes distincts. Seule règle à effet automatique."""
    from annonces.models import Annonce

    distincts = (
        annonce.signalements.filter(auteur__isnull=False)
        .values("auteur")
        .distinct()
        .count()
    )
    if distincts >= settings.ANTISPAM_SEUIL_SIGNALEMENTS and annonce.statut == Annonce.Statut.PUBLIEE:
        annonce.statut = Annonce.Statut.SUSPENDUE
        annonce.save(update_fields=["statut"])
        _marquer(annonce, "AS8", f"{distincts} signalements distincts — masquée en attente de revue")
