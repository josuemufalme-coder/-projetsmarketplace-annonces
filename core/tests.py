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
