"""Charge les motifs de signalement du lancement — SRS §3.7."""

from django.db import migrations

MOTIFS = [
    ("arnaque", "Arnaque présumée", "Likambo ya moyibi", "Suspected scam"),
    ("illicite", "Contenu illicite", "Eloko epekisami", "Illegal content"),
    ("doublon", "Annonce en double", "Annonce ebimi mbala mibale", "Duplicate ad"),
    ("mauvaise-categorie", "Mauvaise catégorie", "Catégorie ya mabe", "Wrong category"),
    ("autre", "Autre problème", "Likambo mosusu", "Other issue"),
]


def charger(apps, schema_editor):
    MotifSignalement = apps.get_model("moderation", "MotifSignalement")
    for ordre, (code, fr, ln, en) in enumerate(MOTIFS, start=1):
        MotifSignalement.objects.get_or_create(
            code=code,
            defaults={"nom_fr": fr, "nom_ln": ln, "nom_en": en, "ordre": ordre},
        )


class Migration(migrations.Migration):
    dependencies = [("moderation", "0001_initial")]

    operations = [migrations.RunPython(charger, migrations.RunPython.noop)]
