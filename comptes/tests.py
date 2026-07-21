from django.test import TestCase
from django.urls import reverse

from geo.models import Commune

from .models import Utilisateur


class ComptesTests(TestCase):
    def _inscrire(self, email="amina@example.com"):
        commune = Commune.objects.get(slug="gombe")
        return self.client.post(
            reverse("comptes:inscription"),
            {
                "email": email,
                "nom_affichage": "Amina",
                "commune": commune.pk,
                "telephone": "+243810000000",
                "password1": "kin2026!solide",
                "password2": "kin2026!solide",
            },
        )

    def test_inscription_cree_et_connecte(self):
        """SRS §3.1 : inscription immédiate, sans vérification SMS (Q3)."""
        reponse = self._inscrire()
        self.assertRedirects(reponse, reverse("core:home"))
        utilisateur = Utilisateur.objects.get(email="amina@example.com")
        self.assertEqual(utilisateur.verification, Utilisateur.Verification.NON_VERIFIE)
        self.assertTrue(utilisateur.is_authenticated)

    def test_email_en_double_refuse(self):
        self._inscrire()
        self.client.logout()
        reponse = self._inscrire()
        self.assertEqual(reponse.status_code, 200)  # formulaire réaffiché avec erreur
        self.assertEqual(Utilisateur.objects.filter(email="amina@example.com").count(), 1)

    def test_connexion_par_email(self):
        """Décision R1 : l'e-mail est l'identifiant de connexion."""
        Utilisateur.objects.create_user(
            email="jo@example.com", password="kin2026!solide", nom_affichage="Jo"
        )
        connecte = self.client.login(username="jo@example.com", password="kin2026!solide")
        self.assertTrue(connecte)

    def test_profil_exige_connexion(self):
        reponse = self.client.get(reverse("comptes:profil"))
        self.assertEqual(reponse.status_code, 302)
        self.assertIn(reverse("comptes:connexion"), reponse.url)

    def test_mise_a_jour_du_profil(self):
        self._inscrire()
        lemba = Commune.objects.get(slug="lemba")
        reponse = self.client.post(
            reverse("comptes:profil"),
            {"nom_affichage": "Amina K.", "commune": lemba.pk, "telephone": ""},
        )
        self.assertRedirects(reponse, reverse("comptes:profil"))
        utilisateur = Utilisateur.objects.get(email="amina@example.com")
        self.assertEqual(utilisateur.nom_affichage, "Amina K.")
        self.assertEqual(utilisateur.commune, lemba)


import re

from django.core import mail


class MotDePasseOublieTests(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="amina@example.com", password="ancien-mdp-2026", nom_affichage="Amina"
        )

    def test_lien_visible_sur_la_page_de_connexion(self):
        reponse = self.client.get(reverse("comptes:connexion"))
        self.assertContains(reponse, "Mot de passe oublié")

    def test_demande_envoie_un_email_avec_lien(self):
        reponse = self.client.post(
            reverse("comptes:mdp_oublie"), {"email": "amina@example.com"}
        )
        self.assertRedirects(reponse, reverse("comptes:mdp_envoye"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("réinitialisation", mail.outbox[0].subject)
        self.assertIn("/compte/mdp-nouveau/", mail.outbox[0].body)

    def test_email_inconnu_ne_revele_rien(self):
        """Même réponse pour une adresse inconnue (pas de fuite d'existence de compte)."""
        reponse = self.client.post(
            reverse("comptes:mdp_oublie"), {"email": "inconnu@example.com"}
        )
        self.assertRedirects(reponse, reverse("comptes:mdp_envoye"))
        self.assertEqual(len(mail.outbox), 0)

    def test_cycle_complet_de_reinitialisation(self):
        self.client.post(reverse("comptes:mdp_oublie"), {"email": "amina@example.com"})
        lien = re.search(r"(/compte/mdp-nouveau/[^\s]+)", mail.outbox[0].body).group(1)
        # Django redirige le lien du jeton vers une URL de session.
        reponse = self.client.get(lien, follow=True)
        self.assertEqual(reponse.status_code, 200)
        url_formulaire = reponse.request["PATH_INFO"]
        reponse = self.client.post(
            url_formulaire,
            {"new_password1": "nouveau-mdp-2026!", "new_password2": "nouveau-mdp-2026!"},
        )
        self.assertRedirects(reponse, reverse("comptes:mdp_termine"))
        self.assertTrue(
            self.client.login(username="amina@example.com", password="nouveau-mdp-2026!")
        )

    def test_lien_invalide_affiche_une_erreur(self):
        reponse = self.client.get("/compte/mdp-nouveau/abc/def-ghi/")
        self.assertContains(reponse, "n'est plus valable")
