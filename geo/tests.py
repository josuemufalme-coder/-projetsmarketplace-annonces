from django.test import TestCase

from .models import Commune, Ville


class ReferentielGeoTests(TestCase):
    def test_kinshasa_seule_ville_active(self):
        """SRS §3.2 : une seule ville active au lancement, Kinshasa."""
        self.assertEqual(Ville.objects.filter(actif=True).count(), 1)
        self.assertEqual(Ville.objects.get(actif=True).nom, "Kinshasa")

    def test_les_24_communes_officielles_sont_chargees(self):
        """Décision R3 : les 24 communes officielles de Kinshasa."""
        kinshasa = Ville.objects.get(slug="kinshasa")
        self.assertEqual(kinshasa.communes.count(), 24)

    def test_communes_connues_presentes(self):
        noms = set(Commune.objects.values_list("nom", flat=True))
        for attendu in ["Gombe", "Lemba", "Masina", "Ngaliema", "Kimbanseke", "Mont-Ngafula"]:
            self.assertIn(attendu, noms)
