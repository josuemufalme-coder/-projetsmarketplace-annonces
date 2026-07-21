from django.test import TestCase
from django.utils import translation

from .models import Categorie


class ReferentielCategoriesTests(TestCase):
    def test_huit_categories_chargees(self):
        """SRS §3.3 : les 8 catégories du lancement."""
        self.assertEqual(Categorie.objects.count(), 8)

    def test_photos_obligatoires_selon_decision_q7(self):
        avec_photos = set(
            Categorie.objects.filter(photos_obligatoires=True).values_list("slug", flat=True)
        )
        self.assertEqual(
            avec_photos,
            {"immobilier", "vehicules", "electronique-telephones", "habits-mode", "maison-jardin"},
        )

    def test_champs_specifiques_immobilier(self):
        immobilier = Categorie.objects.get(slug="immobilier")
        codes = set(immobilier.champs.values_list("code", flat=True))
        self.assertTrue({"type_bien", "transaction", "surface", "pieces"} <= codes)

    def test_champs_specifiques_vehicules(self):
        vehicules = Categorie.objects.get(slug="vehicules")
        codes = set(vehicules.champs.values_list("code", flat=True))
        self.assertTrue({"type_vehicule", "marque", "annee", "kilometrage"} <= codes)
        carburant = vehicules.champs.get(code="carburant")
        self.assertIn("Essence", carburant.options)

    def test_categorie_autres_sans_champ(self):
        self.assertEqual(Categorie.objects.get(slug="autres").champs.count(), 0)

    def test_nom_traduit_selon_la_langue(self):
        vehicules = Categorie.objects.get(slug="vehicules")
        with translation.override("en"):
            self.assertEqual(vehicules.nom, "Vehicles")
        with translation.override("fr"):
            self.assertEqual(vehicules.nom, "Véhicules")

    def test_repli_sur_le_francais_sans_traduction(self):
        """Un libellé sans traduction lingala s'affiche en français (repli SRS §3.9)."""
        champ = Categorie.objects.get(slug="immobilier").champs.get(code="transaction")
        self.assertEqual(champ.nom_ln, "")
        with translation.override("ln"):
            self.assertEqual(champ.nom, champ.nom_fr)
