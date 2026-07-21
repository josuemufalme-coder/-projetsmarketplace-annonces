from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_ok(self):
        """L'accueil répond et présente les sections principales."""
        reponse = self.client.get(reverse("core:home"))
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "Kongo")
        self.assertContains(reponse, "Annonces récentes")

    def test_categories_du_referentiel_affichees(self):
        reponse = self.client.get(reverse("core:home"))
        self.assertContains(reponse, "Immobilier")
        self.assertContains(reponse, "Véhicules")

    def test_language_switch_to_english(self):
        """Le sélecteur de langue bascule bien l'interface en anglais."""
        self.client.post("/i18n/setlang/", {"language": "en"})
        reponse = self.client.get(reverse("core:home"))
        self.assertContains(reponse, "Recent ads")

    def test_language_switch_to_lingala(self):
        self.client.post("/i18n/setlang/", {"language": "ln"})
        reponse = self.client.get(reverse("core:home"))
        self.assertContains(reponse, "Ba annonces ya sika")


from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone

from annonces.models import Annonce, Categorie
from comptes.models import Utilisateur
from geo.models import Commune
from moderation.models import MotifSignalement, Signalement


class LimitationDebitTests(TestCase):
    """SRS §5.3 : limitation de débit sur les actions sensibles."""

    def setUp(self):
        cache.clear()
        self.vendeur = Utilisateur.objects.create_user(
            email="vendeur@example.com", password="kin2026!solide", nom_affichage="Papa Jo"
        )
        self.annonce = Annonce.objects.create(
            vendeur=self.vendeur,
            categorie=Categorie.objects.get(slug="autres"),
            commune=Commune.objects.get(slug="gombe"),
            titre="Objet",
            slug="objet",
            description="Desc.",
            prix=10,
            devise="USD",
            date_publication=timezone.now(),
        )

    @override_settings(RATE_LIMITS={"signalement": (2, 3600)})
    def test_signalements_limites_par_ip(self):
        motif = MotifSignalement.objects.get(code="autre")
        url = reverse("moderation:signaler", args=[self.annonce.pk])
        for _ in range(2):
            reponse = self.client.post(url, {"motif": motif.pk})
            self.assertEqual(reponse.status_code, 302)
        reponse = self.client.post(url, {"motif": motif.pk})
        self.assertEqual(reponse.status_code, 429)
        self.assertEqual(Signalement.objects.count(), 2)

    @override_settings(RATE_LIMITS={"connexion": (3, 900)})
    def test_essais_de_connexion_limites(self):
        url = reverse("comptes:connexion")
        for _ in range(3):
            self.client.post(url, {"username": "x@example.com", "password": "faux"})
        reponse = self.client.post(url, {"username": "x@example.com", "password": "faux"})
        self.assertEqual(reponse.status_code, 429)

    @override_settings(RATE_LIMITS={"connexion": (1, 900)})
    def test_les_get_ne_sont_pas_limites(self):
        url = reverse("comptes:connexion")
        self.client.post(url, {"username": "x@example.com", "password": "faux"})
        reponse = self.client.get(url)
        self.assertEqual(reponse.status_code, 200)

    @override_settings(RATE_LIMITS={"numero": (2, 3600)})
    def test_clics_numero_limites_par_utilisateur(self):
        acheteur = Utilisateur.objects.create_user(
            email="acheteur@example.com", password="kin2026!solide", nom_affichage="Mimi"
        )
        self.client.login(username="acheteur@example.com", password="kin2026!solide")
        url = reverse("annonces:numero", args=[self.annonce.pk])
        self.client.post(url)
        self.client.post(url)
        reponse = self.client.post(url)
        self.assertEqual(reponse.status_code, 429)

    @override_settings(RATE_LIMITS={"inscription": (1, 3600)})
    def test_inscriptions_limitees_par_ip(self):
        url = reverse("comptes:inscription")
        donnees = {
            "email": "a@example.com",
            "nom_affichage": "A",
            "password1": "kin2026!solide",
            "password2": "kin2026!solide",
        }
        self.client.post(url, donnees)
        self.client.logout()  # un robot d'inscription repart anonyme
        donnees["email"] = "b@example.com"
        reponse = self.client.post(url, donnees)
        self.assertEqual(reponse.status_code, 429)
        self.assertFalse(Utilisateur.objects.filter(email="b@example.com").exists())
