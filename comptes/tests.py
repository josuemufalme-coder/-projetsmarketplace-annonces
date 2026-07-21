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
