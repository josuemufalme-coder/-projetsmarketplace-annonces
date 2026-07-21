"""Charge les 8 catégories du lancement et leurs champs spécifiques —
SRS §3.3 et décision Q7 (photos obligatoires selon la catégorie).

Les libellés lingala des catégories sont des premières versions à faire
relire par un locuteur natif ; les libellés de champs sans traduction
s'affichent en français (repli automatique).
"""

from django.db import migrations

# (slug, nom_fr, nom_ln, nom_en, photos_obligatoires, champs)
# champ : (code, nom_fr, nom_en, type, options, unite, obligatoire)
CATEGORIES = [
    ("immobilier", "Immobilier", "Bandako mpe mabele", "Real estate", True, [
        ("type_bien", "Type de bien", "Property type", "liste",
         ["Maison", "Appartement", "Parcelle", "Bureau", "Autre"], "", True),
        ("transaction", "Transaction", "Transaction", "liste",
         ["Vente", "Location"], "", True),
        ("surface", "Surface", "Surface area", "nombre", [], "m²", False),
        ("pieces", "Nombre de pièces", "Number of rooms", "nombre", [], "", False),
    ]),
    ("vehicules", "Véhicules", "Mituka", "Vehicles", True, [
        ("type_vehicule", "Type de véhicule", "Vehicle type", "liste",
         ["Voiture", "Moto", "Camion", "Autre"], "", True),
        ("marque", "Marque", "Brand", "texte", [], "", True),
        ("modele", "Modèle", "Model", "texte", [], "", False),
        ("annee", "Année", "Year", "nombre", [], "", False),
        ("kilometrage", "Kilométrage", "Mileage", "nombre", [], "km", False),
        ("carburant", "Carburant", "Fuel", "liste",
         ["Essence", "Diesel", "Électrique", "Hybride"], "", False),
        ("boite", "Boîte de vitesses", "Gearbox", "liste",
         ["Manuelle", "Automatique"], "", False),
    ]),
    ("electronique-telephones", "Électronique & Téléphones",
     "Elektroniki mpe batelefone", "Electronics & Phones", True, [
        ("type_appareil", "Type d'appareil", "Device type", "liste",
         ["Téléphone", "Tablette", "Ordinateur", "Télévision", "Audio",
          "Console de jeux", "Accessoire", "Autre"], "", True),
        ("marque", "Marque", "Brand", "texte", [], "", False),
        ("etat", "État", "Condition", "liste", ["Neuf", "Occasion"], "", True),
    ]),
    ("habits-mode", "Habits & Mode", "Bilamba mpe monzele", "Clothing & Fashion", True, [
        ("type_article", "Type d'article", "Item type", "texte", [], "", True),
        ("taille", "Taille", "Size", "texte", [], "", False),
        ("etat", "État", "Condition", "liste", ["Neuf", "Occasion"], "", True),
        ("genre", "Genre", "For", "liste", ["Homme", "Femme", "Enfant", "Mixte"], "", False),
    ]),
    ("emploi", "Emploi", "Mosala", "Jobs", False, [
        ("offre_demande", "Offre ou demande", "Offer or request", "liste",
         ["Offre d'emploi", "Demande d'emploi"], "", True),
        ("type_contrat", "Type de contrat", "Contract type", "liste",
         ["CDI", "CDD", "Journalier", "Stage", "Indépendant", "Autre"], "", False),
        ("secteur", "Secteur", "Sector", "texte", [], "", False),
        ("experience", "Expérience", "Experience", "liste",
         ["Débutant", "1 à 3 ans", "3 à 5 ans", "Plus de 5 ans"], "", False),
        ("salaire", "Salaire proposé", "Offered salary", "texte", [], "", False),
    ]),
    ("services", "Services", "Lisungi", "Services", False, [
        ("type_service", "Type de service", "Service type", "texte", [], "", True),
        ("zone", "Zone d'intervention", "Service area", "texte", [], "", False),
    ]),
    ("maison-jardin", "Maison & Jardin", "Ndako mpe elanga", "Home & Garden", True, [
        ("type_article", "Type d'article", "Item type", "texte", [], "", True),
        ("etat", "État", "Condition", "liste", ["Neuf", "Occasion"], "", True),
    ]),
    ("autres", "Autres", "Biloko mosusu", "Other", False, []),
]


def charger(apps, schema_editor):
    Categorie = apps.get_model("annonces", "Categorie")
    ChampCategorie = apps.get_model("annonces", "ChampCategorie")
    for ordre, (slug, nom_fr, nom_ln, nom_en, photos, champs) in enumerate(CATEGORIES, start=1):
        categorie, _ = Categorie.objects.get_or_create(
            slug=slug,
            defaults={
                "nom_fr": nom_fr,
                "nom_ln": nom_ln,
                "nom_en": nom_en,
                "ordre": ordre,
                "photos_obligatoires": photos,
            },
        )
        for c_ordre, (code, c_fr, c_en, c_type, options, unite, oblig) in enumerate(champs, start=1):
            ChampCategorie.objects.get_or_create(
                categorie=categorie,
                code=code,
                defaults={
                    "nom_fr": c_fr,
                    "nom_en": c_en,
                    "type": c_type,
                    "options": options,
                    "unite": unite,
                    "obligatoire": oblig,
                    "ordre": c_ordre,
                },
            )


class Migration(migrations.Migration):
    dependencies = [("annonces", "0001_initial")]

    operations = [migrations.RunPython(charger, migrations.RunPython.noop)]
