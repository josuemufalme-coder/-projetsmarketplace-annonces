import datetime

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from annonces.models import Annonce, Categorie
from comptes.models import Utilisateur
from geo.models import Commune

from .antispam import est_doublon_strict, evaluer_annonce, evaluer_signalements
from .models import MarqueAntiSpam, MotifFrauduleux, MotifSignalement, Signalement


class BaseModerationTests(TestCase):
    def setUp(self):
        self.vendeur = Utilisateur.objects.create_user(
            email="vendeur@example.com", password="kin2026!solide", nom_affichage="Papa Jo"
        )
        # Compte ancien par défaut (échappe à la règle AS2).
        Utilisateur.objects.filter(pk=self.vendeur.pk).update(
            date_joined=timezone.now() - datetime.timedelta(days=30)
        )
        self.vendeur.refresh_from_db()
        self.gombe = Commune.objects.get(slug="gombe")

    def creer_annonce(self, titre="Objet", **surcharges):
        valeurs = {
            "vendeur": self.vendeur,
            "categorie": Categorie.objects.get(slug="autres"),
            "commune": self.gombe,
            "titre": titre,
            "slug": "objet",
            "description": f"Description de {titre}.",
            "prix": 10,
            "devise": "USD",
            "date_publication": timezone.now(),
        }
        valeurs.update(surcharges)
        return Annonce.objects.create(**valeurs)


class ReglesAntiSpamTests(BaseModerationTests):
    def test_motifs_de_signalement_charges(self):
        self.assertEqual(MotifSignalement.objects.count(), 5)

    def test_as1_publication_en_rafale(self):
        for i in range(6):
            annonce = self.creer_annonce(titre=f"Objet {i}")
        evaluer_annonce(annonce)
        self.assertTrue(MarqueAntiSpam.objects.filter(annonce=annonce, regle="AS1").exists())

    def test_as3_doublon_strict_detecte(self):
        self.creer_annonce(titre="Vélo", description="Comme neuf.")
        self.assertTrue(est_doublon_strict(self.vendeur, "Vélo", "Comme neuf."))
        self.assertFalse(est_doublon_strict(self.vendeur, "Vélo", "Autre description."))

    def test_as5_motif_frauduleux(self):
        MotifFrauduleux.objects.create(expression="paiement d'avance")
        annonce = self.creer_annonce(
            titre="Téléphone", description="Envoyez un paiement d'avance avant la visite."
        )
        evaluer_annonce(annonce)
        self.assertTrue(MarqueAntiSpam.objects.filter(annonce=annonce, regle="AS5").exists())

    def test_as6_lien_dans_le_titre(self):
        annonce = self.creer_annonce(titre="Voir www.arnaque.example")
        evaluer_annonce(annonce)
        self.assertTrue(MarqueAntiSpam.objects.filter(annonce=annonce, regle="AS6").exists())

    def test_as7_prix_aberrant_vehicule(self):
        annonce = self.creer_annonce(
            titre="Voiture pas chère",
            categorie=Categorie.objects.get(slug="vehicules"),
            prix=10,
            devise="USD",
        )
        evaluer_annonce(annonce)
        self.assertTrue(MarqueAntiSpam.objects.filter(annonce=annonce, regle="AS7").exists())

    def test_annonce_normale_sans_marque(self):
        """Un utilisateur légitime ne déclenche rien (principe de l'Annexe A)."""
        annonce = self.creer_annonce(titre="Chaise en bois", prix=15)
        evaluer_annonce(annonce)
        self.assertFalse(MarqueAntiSpam.objects.filter(annonce=annonce).exists())


class SignalementTests(BaseModerationTests):
    def test_signalement_par_un_visiteur_sans_compte(self):
        """SRS §3.7 : le signalement est ouvert aux visiteurs."""
        annonce = self.creer_annonce()
        motif = MotifSignalement.objects.get(code="arnaque")
        reponse = self.client.post(
            reverse("moderation:signaler", args=[annonce.pk]),
            {"motif": motif.pk, "commentaire": "Prix trop beau pour être vrai."},
        )
        self.assertRedirects(reponse, annonce.get_absolute_url())
        signalement = Signalement.objects.get(annonce=annonce)
        self.assertIsNone(signalement.auteur)
        self.assertEqual(signalement.statut, Signalement.Statut.EN_ATTENTE)

    @override_settings(ANTISPAM_SEUIL_SIGNALEMENTS=3)
    def test_as8_masquage_apres_signalements_distincts(self):
        annonce = self.creer_annonce()
        motif = MotifSignalement.objects.get(code="arnaque")
        for i in range(3):
            auteur = Utilisateur.objects.create_user(
                email=f"u{i}@example.com", password="kin2026!solide", nom_affichage=f"U{i}"
            )
            Signalement.objects.create(annonce=annonce, auteur=auteur, motif=motif)
        evaluer_signalements(annonce)
        annonce.refresh_from_db()
        self.assertEqual(annonce.statut, Annonce.Statut.SUSPENDUE)
        self.assertTrue(MarqueAntiSpam.objects.filter(annonce=annonce, regle="AS8").exists())

    @override_settings(ANTISPAM_SEUIL_SIGNALEMENTS=3)
    def test_as8_ignore_les_signalements_anonymes_repetes(self):
        """Le masquage exige des comptes distincts, pas des signalements anonymes."""
        annonce = self.creer_annonce()
        motif = MotifSignalement.objects.get(code="arnaque")
        for _ in range(5):
            Signalement.objects.create(annonce=annonce, auteur=None, motif=motif)
        evaluer_signalements(annonce)
        annonce.refresh_from_db()
        self.assertEqual(annonce.statut, Annonce.Statut.PUBLIEE)

    def test_annonce_suspendue_invisible(self):
        annonce = self.creer_annonce(statut=Annonce.Statut.SUSPENDUE)
        reponse = self.client.get(reverse("annonces:liste"))
        self.assertNotContains(reponse, annonce.titre)
