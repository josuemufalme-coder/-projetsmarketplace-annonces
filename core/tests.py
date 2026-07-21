from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_ok(self):
        """La page d'accueil répond et porte le nom du site."""
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kongo")

    def test_home_default_language_is_french(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Bientôt disponible")

    def test_language_switch_to_english(self):
        """Le sélecteur de langue bascule bien l'interface en anglais."""
        self.client.post("/i18n/setlang/", {"language": "en"})
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Coming soon")

    def test_language_switch_to_lingala(self):
        self.client.post("/i18n/setlang/", {"language": "ln"})
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Ekomonana kala mingi te")
