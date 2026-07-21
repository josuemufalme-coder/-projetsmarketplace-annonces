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


import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from comptes.models import Utilisateur
from geo.models import Commune

from .models import Annonce, ClicAffichageNumero, Photo

# GIF 1×1 valide, suffisant pour tester l'envoi de photos.
GIF_MINUSCULE = (
    b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00"
    b"\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


def photo_test(nom="photo.gif"):
    return SimpleUploadedFile(nom, GIF_MINUSCULE, content_type="image/gif")


class BaseAnnonceTests(TestCase):
    def setUp(self):
        self.vendeur = Utilisateur.objects.create_user(
            email="vendeur@example.com",
            password="kin2026!solide",
            nom_affichage="Papa Jo",
            telephone="+243811111111",
        )
        self.gombe = Commune.objects.get(slug="gombe")

    def creer_annonce(self, **surcharges):
        valeurs = {
            "vendeur": self.vendeur,
            "categorie": Categorie.objects.get(slug="autres"),
            "commune": self.gombe,
            "titre": "Objet à vendre",
            "slug": "objet-a-vendre",
            "description": "Description de test.",
            "prix": 100,
            "devise": "USD",
            "contact": Annonce.Contact.TELEPHONE,
            "date_publication": timezone.now(),
        }
        valeurs.update(surcharges)
        return Annonce.objects.create(**valeurs)


class PublicationTests(BaseAnnonceTests):
    def _publier_vehicule(self, **surcharges):
        self.client.login(username="vendeur@example.com", password="kin2026!solide")
        donnees = {
            "titre": "Toyota RAV4 2015",
            "description": "Bon état général, entretien suivi.",
            "commune": self.gombe.pk,
            "prix": "8500",
            "devise": "USD",
            "contact": "telephone",
            "telephone": "+243811111111",
            "champ_type_vehicule": "Voiture",
            "champ_marque": "Toyota",
            "champ_annee": "2015",
            "champ_kilometrage": "95000",
            "photos": photo_test(),
        }
        donnees.update(surcharges)
        return self.client.post(
            reverse("annonces:publier_categorie", args=["vehicules"]), donnees
        )

    def test_publication_exige_connexion(self):
        reponse = self.client.get(reverse("annonces:publier"))
        self.assertEqual(reponse.status_code, 302)

    def test_publication_complete(self):
        reponse = self._publier_vehicule()
        annonce = Annonce.objects.get(titre="Toyota RAV4 2015")
        self.assertRedirects(reponse, annonce.get_absolute_url())
        self.assertEqual(annonce.statut, Annonce.Statut.PUBLIEE)  # publication immédiate (Q2)
        self.assertEqual(annonce.attributs["marque"], "Toyota")
        self.assertEqual(annonce.attributs["annee"], 2015)
        self.assertEqual(annonce.photos.count(), 1)

    def test_photo_obligatoire_pour_vehicules(self):
        """Décision Q7 : pas de véhicule sans photo."""
        reponse = self._publier_vehicule(photos="")
        self.assertEqual(reponse.status_code, 200)
        self.assertFalse(Annonce.objects.filter(titre="Toyota RAV4 2015").exists())

    def test_prix_ou_a_discuter_obligatoire(self):
        """Décision Q8 : un prix + devise, ou « à discuter »."""
        reponse = self._publier_vehicule(prix="", devise="")
        self.assertEqual(reponse.status_code, 200)
        self.assertFalse(Annonce.objects.exists())
        reponse = self._publier_vehicule(prix="", devise="", prix_a_discuter="on")
        annonce = Annonce.objects.get(titre="Toyota RAV4 2015")
        self.assertTrue(annonce.prix_a_discuter)
        self.assertIsNone(annonce.prix)

    def test_numero_requis_en_mode_telephone(self):
        self.vendeur.telephone = ""
        self.vendeur.save()
        reponse = self._publier_vehicule(telephone="")
        self.assertEqual(reponse.status_code, 200)
        self.assertFalse(Annonce.objects.exists())


class VisibiliteTests(BaseAnnonceTests):
    def test_liste_montre_les_annonces_actives(self):
        annonce = self.creer_annonce()
        reponse = self.client.get(reverse("annonces:liste"))
        self.assertContains(reponse, annonce.titre)

    def test_annonce_expiree_invisible_en_liste(self):
        """SRS §3.3 : expiration automatique à 30 jours."""
        self.creer_annonce(date_publication=timezone.now() - datetime.timedelta(days=31))
        reponse = self.client.get(reverse("annonces:liste"))
        self.assertNotContains(reponse, "Objet à vendre")

    def test_annonce_retiree_invisible_pour_le_public(self):
        annonce = self.creer_annonce(statut=Annonce.Statut.RETIREE)
        reponse = self.client.get(annonce.get_absolute_url())
        self.assertEqual(reponse.status_code, 404)

    def test_filtre_par_commune_et_categorie(self):
        self.creer_annonce()
        lemba = Commune.objects.get(slug="lemba")
        self.creer_annonce(titre="Autre objet", commune=lemba)
        reponse = self.client.get(reverse("annonces:liste"), {"commune": "gombe"})
        self.assertContains(reponse, "Objet à vendre")
        self.assertNotContains(reponse, "Autre objet")

    def test_filtre_prix_par_devise(self):
        """Décision Q4 : fourchette de prix au sein d'une devise."""
        self.creer_annonce(titre="Cher", prix=5000, devise="USD")
        self.creer_annonce(titre="Abordable", prix=50, devise="USD")
        self.creer_annonce(titre="En francs", prix=100000, devise="CDF")
        reponse = self.client.get(
            reverse("annonces:liste"), {"devise": "USD", "prix_max": "100"}
        )
        self.assertContains(reponse, "Abordable")
        self.assertNotContains(reponse, "Cher")
        self.assertNotContains(reponse, "En francs")


class NumeroTests(BaseAnnonceTests):
    def test_numero_absent_sans_clic(self):
        """Décision Q9 : le numéro n'est jamais dans le HTML initial."""
        annonce = self.creer_annonce()
        reponse = self.client.get(annonce.get_absolute_url())
        self.assertNotContains(reponse, self.vendeur.telephone)

    def test_clic_exige_connexion(self):
        annonce = self.creer_annonce()
        reponse = self.client.post(reverse("annonces:numero", args=[annonce.pk]))
        self.assertEqual(reponse.status_code, 302)

    def test_clic_revele_et_journalise(self):
        """Décisions Q1/Q9 : clic authentifié, journalisé, numéro révélé."""
        annonce = self.creer_annonce()
        acheteur = Utilisateur.objects.create_user(
            email="acheteur@example.com", password="kin2026!solide", nom_affichage="Mimi"
        )
        self.client.login(username="acheteur@example.com", password="kin2026!solide")
        reponse = self.client.post(reverse("annonces:numero", args=[annonce.pk]))
        self.assertContains(reponse, self.vendeur.telephone)
        self.assertTrue(
            ClicAffichageNumero.objects.filter(annonce=annonce, utilisateur=acheteur).exists()
        )
        # Un second clic ne crée pas de doublon.
        self.client.post(reverse("annonces:numero", args=[annonce.pk]))
        self.assertEqual(ClicAffichageNumero.objects.count(), 1)


class CycleDeVieTests(BaseAnnonceTests):
    def test_renouvellement_limite_a_7_jours(self):
        """Décision Q10 : pas de renouvellement avant 7 jours."""
        annonce = self.creer_annonce()
        self.assertFalse(annonce.peut_renouveler)
        annonce.date_publication = timezone.now() - datetime.timedelta(days=8)
        annonce.save()
        self.assertTrue(annonce.peut_renouveler)

    def test_renouveler_remonte_l_annonce(self):
        annonce = self.creer_annonce(
            date_publication=timezone.now() - datetime.timedelta(days=25)
        )
        self.client.login(username="vendeur@example.com", password="kin2026!solide")
        self.client.post(reverse("annonces:renouveler", args=[annonce.pk]))
        annonce.refresh_from_db()
        self.assertLess(timezone.now() - annonce.date_publication, datetime.timedelta(minutes=1))

    def test_retirer_son_annonce(self):
        annonce = self.creer_annonce()
        self.client.login(username="vendeur@example.com", password="kin2026!solide")
        self.client.post(reverse("annonces:retirer", args=[annonce.pk]))
        annonce.refresh_from_db()
        self.assertEqual(annonce.statut, Annonce.Statut.RETIREE)

    def test_impossible_de_retirer_l_annonce_d_autrui(self):
        annonce = self.creer_annonce()
        Utilisateur.objects.create_user(
            email="autre@example.com", password="kin2026!solide", nom_affichage="Autre"
        )
        self.client.login(username="autre@example.com", password="kin2026!solide")
        reponse = self.client.post(reverse("annonces:retirer", args=[annonce.pk]))
        self.assertEqual(reponse.status_code, 404)


class RedimensionnementPhotosTests(BaseAnnonceTests):
    """Étape 12 : les photos sont réduites et une vignette est générée (SRS §5.2)."""

    def _photo_haute_resolution(self):
        import io

        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        image = Image.new("RGB", (3000, 2000), (10, 120, 80))
        tampon = io.BytesIO()
        image.save(tampon, format="PNG")
        return SimpleUploadedFile("grande-photo.png", tampon.getvalue(), content_type="image/png")

    def test_image_reduite_et_vignette_creee(self):
        from PIL import Image

        annonce = self.creer_annonce()
        photo = Photo(annonce=annonce, ordre=1)
        photo.image = self._photo_haute_resolution()
        photo.save()

        avec_image = Image.open(photo.image)
        self.assertLessEqual(max(avec_image.size), 1600)
        self.assertEqual(avec_image.format, "JPEG")
        self.assertTrue(photo.vignette)
        avec_vignette = Image.open(photo.vignette)
        self.assertLessEqual(max(avec_vignette.size), 500)
        self.assertLess(photo.vignette.size, photo.image.size)

    def test_la_liste_utilise_la_vignette(self):
        annonce = self.creer_annonce()
        photo = Photo(annonce=annonce, ordre=1)
        photo.image = self._photo_haute_resolution()
        photo.save()
        reponse = self.client.get(reverse("annonces:liste"))
        self.assertContains(reponse, "vignettes/")
