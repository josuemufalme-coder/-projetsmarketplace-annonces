"""Charge Kinshasa (seule ville active au lancement) et ses 24 communes
officielles — décision R3 du cahier des charges."""

from django.db import migrations
from django.utils.text import slugify

COMMUNES = [
    "Bandalungwa", "Barumbu", "Bumbu", "Gombe", "Kalamu", "Kasa-Vubu",
    "Kimbanseke", "Kinshasa", "Kintambo", "Kisenso", "Lemba", "Limete",
    "Lingwala", "Makala", "Maluku", "Masina", "Matete", "Mont-Ngafula",
    "Ndjili", "Ngaba", "Ngaliema", "Ngiri-Ngiri", "Nsele", "Selembao",
]


def charger(apps, schema_editor):
    Ville = apps.get_model("geo", "Ville")
    Commune = apps.get_model("geo", "Commune")
    kinshasa, _ = Ville.objects.get_or_create(
        slug="kinshasa", defaults={"nom": "Kinshasa", "actif": True}
    )
    for nom in COMMUNES:
        Commune.objects.get_or_create(
            ville=kinshasa, slug=slugify(nom), defaults={"nom": nom}
        )


class Migration(migrations.Migration):
    dependencies = [("geo", "0001_initial")]

    operations = [migrations.RunPython(charger, migrations.RunPython.noop)]
