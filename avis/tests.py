from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from annonces.models import Annonce, Categorie, ClicAffichageNumero
from comptes.models import Utilisateur
from geo.models import Commune
from messagerie.models import Conversation, Message

from .models import Avis, peut_laisser_avis


class AvisTests(TestCase):
    def setUp(self):
        self.vendeur = Utilisateur.objects.create_user(
            email="vendeur@example.com", password="kin2026!solide", nom_affichage="Papa Jo"
        )
        self.acheteur = Utilisateur.objects.create_user(
            email="acheteur@example.com", password="kin2026!solide", nom_affichage="Mimi"
        )
        self.annonce = Annonce.objects.create(
            vendeur=self.vendeur,
            categorie=Categorie.objects.get(slug="autres"),
            commune=Commune.objects.get(slug="gombe"),
            titre="Table en bois",
            slug="table-en-bois",
            description="Solide.",
            prix=40,
            devise="USD",
            date_publication=timezone.now(),
        )

    def _poster_avis(self, note="5", commentaire="Très fiable."):
        return self.client.post(
            reverse("avis:laisser", args=[self.vendeur.pk]),
            {"note": note, "commentaire": commentaire},
        )

    def test_refus_sans_contact_trace(self):
        """Décision Q1 : pas d'avis sans contact tracé sur la plateforme."""
        self.assertFalse(peut_laisser_avis(self.acheteur, self.vendeur))
        self.client.login(username="acheteur@example.com", password="kin2026!solide")
        self._poster_avis()
        self.assertEqual(Avis.objects.count(), 0)

    def test_autorise_apres_clic_numero(self):
        ClicAffichageNumero.objects.create(annonce=self.annonce, utilisateur=self.acheteur)
        self.assertTrue(peut_laisser_avis(self.acheteur, self.vendeur))
        self.client.login(username="acheteur@example.com", password="kin2026!solide")
        self._poster_avis()
        avis = Avis.objects.get(auteur=self.acheteur, vendeur=self.vendeur)
        self.assertEqual(avis.note, 5)

    def test_autorise_apres_message_interne(self):
        fil = Conversation.objects.create(annonce=self.annonce, acheteur=self.acheteur)
        Message.objects.create(conversation=fil, expediteur=self.acheteur, texte="Dispo ?")
        self.assertTrue(peut_laisser_avis(self.acheteur, self.vendeur))

    def test_un_seul_avis_modifiable(self):
        """SRS §3.6 : un avis par couple, modifiable."""
        ClicAffichageNumero.objects.create(annonce=self.annonce, utilisateur=self.acheteur)
        self.client.login(username="acheteur@example.com", password="kin2026!solide")
        self._poster_avis(note="2", commentaire="Bof.")
        self._poster_avis(note="4", commentaire="Finalement très bien.")
        self.assertEqual(Avis.objects.count(), 1)
        self.assertEqual(Avis.objects.get().note, 4)

    def test_pas_d_avis_sur_soi_meme(self):
        self.assertFalse(peut_laisser_avis(self.vendeur, self.vendeur))

    def test_note_moyenne_sur_le_profil(self):
        autre = Utilisateur.objects.create_user(
            email="autre@example.com", password="kin2026!solide", nom_affichage="Autre"
        )
        Avis.objects.create(auteur=self.acheteur, vendeur=self.vendeur, note=5)
        Avis.objects.create(auteur=autre, vendeur=self.vendeur, note=3)
        self.assertEqual(self.vendeur.note_moyenne, 4)
        reponse = self.client.get(reverse("comptes:vendeur", args=[self.vendeur.pk]))
        self.assertContains(reponse, "4,0/5")

    def test_profil_public_montre_annonces_actives(self):
        reponse = self.client.get(reverse("comptes:vendeur", args=[self.vendeur.pk]))
        self.assertContains(reponse, "Table en bois")
