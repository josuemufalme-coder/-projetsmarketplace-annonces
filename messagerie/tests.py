from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from annonces.models import Annonce, Categorie
from comptes.models import Utilisateur
from geo.models import Commune

from .models import Conversation, Message


class MessagerieTests(TestCase):
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
            titre="Vélo de ville",
            slug="velo-de-ville",
            description="Bon état.",
            prix_a_discuter=True,
            contact=Annonce.Contact.MESSAGERIE,
            date_publication=timezone.now(),
        )

    def _contacter(self, texte="Bonjour, toujours disponible ?"):
        return self.client.post(
            reverse("messagerie:contacter", args=[self.annonce.pk]), {"texte": texte}
        )

    def test_contact_exige_connexion(self):
        reponse = self._contacter()
        self.assertEqual(reponse.status_code, 302)
        self.assertIn(reverse("comptes:connexion"), reponse.url)

    def test_premier_message_cree_le_fil_et_notifie_par_email(self):
        """Décision Q5 : notification e-mail au destinataire."""
        self.client.login(username="acheteur@example.com", password="kin2026!solide")
        self._contacter()
        fil = Conversation.objects.get(annonce=self.annonce, acheteur=self.acheteur)
        self.assertEqual(fil.messages.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["vendeur@example.com"])
        self.assertIn("Vélo de ville", mail.outbox[0].subject)

    def test_regroupement_des_notifications(self):
        """Pas de second e-mail tant que le premier message n'est pas lu (SRS §3.5)."""
        self.client.login(username="acheteur@example.com", password="kin2026!solide")
        self._contacter()
        fil = Conversation.objects.get(annonce=self.annonce)
        self.client.post(reverse("messagerie:conversation", args=[fil.pk]), {"texte": "Relance"})
        self.assertEqual(fil.messages.count(), 2)
        self.assertEqual(len(mail.outbox), 1)

    def test_reponse_du_vendeur_notifie_l_acheteur_et_marque_lu(self):
        self.client.login(username="acheteur@example.com", password="kin2026!solide")
        self._contacter()
        fil = Conversation.objects.get(annonce=self.annonce)
        self.client.logout()

        self.client.login(username="vendeur@example.com", password="kin2026!solide")
        self.client.get(reverse("messagerie:conversation", args=[fil.pk]))  # lecture
        self.assertFalse(fil.non_lus_pour(self.vendeur).exists())
        self.client.post(reverse("messagerie:conversation", args=[fil.pk]), {"texte": "Oui !"})
        self.assertEqual(mail.outbox[-1].to, ["acheteur@example.com"])

    def test_vendeur_ne_peut_pas_se_contacter(self):
        self.client.login(username="vendeur@example.com", password="kin2026!solide")
        self._contacter()
        self.assertFalse(Conversation.objects.exists())

    def test_pas_de_messagerie_en_mode_telephone(self):
        """SRS §3.5 : le mode de contact choisi par le vendeur est respecté."""
        self.annonce.contact = Annonce.Contact.TELEPHONE
        self.annonce.save()
        self.client.login(username="acheteur@example.com", password="kin2026!solide")
        self._contacter()
        self.assertFalse(Conversation.objects.exists())

    def test_fil_inaccessible_aux_tiers(self):
        self.client.login(username="acheteur@example.com", password="kin2026!solide")
        self._contacter()
        fil = Conversation.objects.get(annonce=self.annonce)
        Utilisateur.objects.create_user(
            email="tiers@example.com", password="kin2026!solide", nom_affichage="Tiers"
        )
        self.client.logout()
        self.client.login(username="tiers@example.com", password="kin2026!solide")
        reponse = self.client.get(reverse("messagerie:conversation", args=[fil.pk]))
        self.assertRedirects(reponse, reverse("messagerie:boite"))

    def test_compteur_de_non_lus_dans_l_entete(self):
        self.client.login(username="acheteur@example.com", password="kin2026!solide")
        self._contacter()
        self.client.logout()
        self.client.login(username="vendeur@example.com", password="kin2026!solide")
        reponse = self.client.get(reverse("core:home"))
        self.assertContains(reponse, 'class="badge"')
