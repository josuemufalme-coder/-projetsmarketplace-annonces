"""Charge un jeu de données de démonstration pour la recette manuelle.

Usage : python manage.py charger_demo
Idempotent : relancer la commande ne crée pas de doublons.
Tous les comptes de démonstration ont le mot de passe « demo2026! ».
"""

import io
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from PIL import Image, ImageDraw

from annonces.models import Annonce, Categorie, Photo
from comptes.models import Utilisateur
from geo.models import Commune

MOT_DE_PASSE = "demo2026!"

UTILISATEURS = [
    ("chantal@demo.cd", "Chantal M.", "gombe", "+243810000001"),
    ("didier@demo.cd", "Didier K.", "lemba", "+243810000002"),
    ("patrick@demo.cd", "Patrick N.", "masina", "+243810000003"),
    ("grace@demo.cd", "Grâce L.", "limete", "+243810000004"),
]

# (vendeur, catégorie, commune, titre, description, prix, devise, à_discuter,
#  contact, attributs, couleur_photo)
ANNONCES = [
    ("chantal@demo.cd", "electronique-telephones", "gombe",
     "iPhone 12 128 Go très bon état",
     "iPhone 12 débloqué tout réseau, batterie 88 %, livré avec câble. Visible à Gombe.",
     380, "USD", False, "telephone",
     {"type_appareil": "Téléphone", "marque": "Apple", "etat": "Occasion"}, (52, 120, 246)),
    ("chantal@demo.cd", "electronique-telephones", "gombe",
     "Ordinateur portable HP EliteBook",
     "HP EliteBook 840 G5, i5, 8 Go RAM, SSD 256 Go. Idéal étudiant ou bureau.",
     260, "USD", False, "telephone",
     {"type_appareil": "Ordinateur", "marque": "HP", "etat": "Occasion"}, (90, 90, 100)),
    ("chantal@demo.cd", "electronique-telephones", "gombe",
     "Téléviseur Samsung 43 pouces",
     "Smart TV Samsung 43\" Full HD, très peu servie, avec télécommande.",
     220, "USD", False, "messagerie",
     {"type_appareil": "Télévision", "marque": "Samsung", "etat": "Occasion"}, (20, 20, 30)),
    ("didier@demo.cd", "immobilier", "mont-ngafula",
     "Parcelle 20 × 30 à Mont-Ngafula",
     "Parcelle de 600 m² avec documents en règle, quartier calme, accès facile.",
     15000, "USD", False, "telephone",
     {"type_bien": "Parcelle", "transaction": "Vente", "surface": 600}, (167, 130, 74)),
    ("didier@demo.cd", "immobilier", "gombe",
     "Appartement 3 pièces à louer à Gombe",
     "Appartement meublé, 2 chambres + salon, groupe électrogène, parking. Loyer mensuel.",
     800, "USD", False, "messagerie",
     {"type_bien": "Appartement", "transaction": "Location", "pieces": 3, "surface": 95}, (120, 160, 200)),
    ("didier@demo.cd", "vehicules", "lemba",
     "Toyota RAV4 2014",
     "RAV4 essence, boîte automatique, climatisation, 98 000 km, entretien suivi.",
     8500, "USD", False, "telephone",
     {"type_vehicule": "Voiture", "marque": "Toyota", "modele": "RAV4",
      "annee": 2014, "kilometrage": 98000, "carburant": "Essence", "boite": "Automatique"}, (140, 30, 30)),
    ("patrick@demo.cd", "vehicules", "masina",
     "Moto TVS presque neuve",
     "Moto TVS 2023, 5 200 km, papiers en ordre. Parfaite pour taxi-moto.",
     1300000, "CDF", False, "telephone",
     {"type_vehicule": "Moto", "marque": "TVS", "annee": 2023, "kilometrage": 5200}, (230, 90, 30)),
    ("patrick@demo.cd", "services", "masina",
     "Mécanicien à domicile Masina et environs",
     "Réparation et entretien de véhicules à domicile : freins, vidange, embrayage, diagnostic.",
     None, "", True, "telephone",
     {"type_service": "Mécanique automobile", "zone": "Masina, Ndjili, Limete"}, (60, 60, 60)),
    ("patrick@demo.cd", "emploi", "masina",
     "Cherche apprenti mécanicien",
     "Atelier à Masina cherche un apprenti motivé. Formation assurée, petite prime au début.",
     None, "", True, "messagerie",
     {"offre_demande": "Offre d'emploi", "type_contrat": "Autre", "secteur": "Mécanique",
      "experience": "Débutant"}, (30, 100, 60)),
    ("grace@demo.cd", "habits-mode", "limete",
     "Robes en pagne wax sur mesure",
     "Confection de robes en wax, modèles modernes, livraison sous une semaine.",
     45000, "CDF", False, "messagerie",
     {"type_article": "Robe", "etat": "Neuf", "genre": "Femme"}, (200, 60, 130)),
    ("grace@demo.cd", "maison-jardin", "limete",
     "Canapé 3 places + 2 fauteuils",
     "Salon complet en tissu, bon état général, à venir chercher à Limete.",
     350, "USD", False, "telephone",
     {"type_article": "Salon", "etat": "Occasion"}, (110, 80, 50)),
    ("grace@demo.cd", "autres", "limete",
     "Cartons de déménagement gratuits",
     "Une vingtaine de cartons solides à donner après déménagement.",
     None, "", True, "messagerie", {}, (150, 150, 120)),
]


def image_demo(couleur, texte):
    """Génère une image JPEG simple (aplat + bandeau) pour la démonstration."""
    image = Image.new("RGB", (800, 600), couleur)
    dessin = ImageDraw.Draw(image)
    fonce = tuple(max(0, c - 40) for c in couleur)
    dessin.rectangle([0, 480, 800, 600], fill=fonce)
    dessin.text((24, 510), texte[:40], fill=(255, 255, 255))
    tampon = io.BytesIO()
    image.save(tampon, format="JPEG", quality=80)
    return ContentFile(tampon.getvalue())


class Command(BaseCommand):
    help = "Charge des comptes et annonces de démonstration (mot de passe : demo2026!)."

    def handle(self, *args, **options):
        random.seed(42)
        comptes = {}
        for email, nom, commune_slug, telephone in UTILISATEURS:
            utilisateur = Utilisateur.objects.filter(email=email).first()
            if not utilisateur:
                utilisateur = Utilisateur.objects.create_user(
                    email=email,
                    password=MOT_DE_PASSE,
                    nom_affichage=nom,
                    telephone=telephone,
                    commune=Commune.objects.get(slug=commune_slug),
                )
                self.stdout.write(f"Compte créé : {email}")
            comptes[email] = utilisateur

        for (email, cat, commune_slug, titre, description, prix, devise,
             a_discuter, contact, attributs, couleur) in ANNONCES:
            if Annonce.objects.filter(titre=titre).exists():
                continue
            annonce = Annonce.objects.create(
                vendeur=comptes[email],
                categorie=Categorie.objects.get(slug=cat),
                commune=Commune.objects.get(slug=commune_slug),
                titre=titre,
                slug=slugify(titre)[:140] or "annonce",
                description=description,
                prix=prix,
                devise=devise,
                prix_a_discuter=a_discuter,
                contact=contact,
                attributs=attributs,
                date_publication=timezone.now()
                - timezone.timedelta(hours=random.randint(1, 240)),
            )
            for ordre in (1, 2):
                nuance = tuple(min(255, c + (ordre - 1) * 25) for c in couleur)
                photo = Photo(annonce=annonce, ordre=ordre)
                photo.image.save(
                    f"demo-{annonce.pk}-{ordre}.jpg", image_demo(nuance, titre), save=True
                )
            self.stdout.write(f"Annonce créée : {titre}")

        self.stdout.write(self.style.SUCCESS(
            f"Terminé : {Utilisateur.objects.filter(email__endswith='@demo.cd').count()} comptes, "
            f"{Annonce.objects.count()} annonces au total."
        ))
