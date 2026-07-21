"""Référentiel des catégories et de leurs champs spécifiques — SRS §3.3.

Chaque catégorie porte son paramètre « photos obligatoires » (décision Q7)
et ses champs spécifiques structurés (surface, kilométrage…), définis en
base : ajouter un champ à une catégorie se fait depuis l'administration,
sans migration. Le modèle Annonce lui-même arrivera à l'étape suivante.
"""

from django.db import models
from django.utils.translation import get_language


class ReferentielTraduisible(models.Model):
    """Libellé traduisible fr/ln/en ; le français sert de repli (SRS §3.9)."""

    nom_fr = models.CharField("nom (français)", max_length=100)
    nom_ln = models.CharField("nom (lingala)", max_length=100, blank=True)
    nom_en = models.CharField("nom (anglais)", max_length=100, blank=True)

    class Meta:
        abstract = True

    @property
    def nom(self):
        langue = (get_language() or "fr")[:2]
        return getattr(self, f"nom_{langue}", "") or self.nom_fr

    def __str__(self):
        return self.nom_fr


class Categorie(ReferentielTraduisible):
    slug = models.SlugField(unique=True)
    ordre = models.PositiveSmallIntegerField(default=0)
    photos_obligatoires = models.BooleanField(
        default=False,
        help_text="Au moins une photo exigée à la publication (décision Q7).",
    )
    actif = models.BooleanField("active", default=True)

    class Meta:
        verbose_name = "catégorie"
        ordering = ["ordre", "nom_fr"]


class ChampCategorie(ReferentielTraduisible):
    """Définition d'un champ spécifique d'une catégorie (« DéfinitionDeChamp » du SRS §4)."""

    class Type(models.TextChoices):
        TEXTE = "texte", "Texte"
        NOMBRE = "nombre", "Nombre"
        LISTE = "liste", "Liste de valeurs"

    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name="champs")
    code = models.SlugField(
        "code technique",
        help_text="Identifiant stable du champ, utilisé pour stocker les valeurs des annonces.",
    )
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.TEXTE)
    options = models.JSONField(
        default=list,
        blank=True,
        help_text="Valeurs proposées pour un champ de type « liste » (une par ligne).",
    )
    unite = models.CharField("unité", max_length=20, blank=True, help_text="Ex. : m², km")
    obligatoire = models.BooleanField(default=False)
    ordre = models.PositiveSmallIntegerField(default=0)
    actif = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "champ de catégorie"
        verbose_name_plural = "champs de catégorie"
        ordering = ["ordre"]
        constraints = [
            models.UniqueConstraint(fields=["categorie", "code"], name="champ_code_unique_par_categorie"),
        ]


class AnnonceQuerySet(models.QuerySet):
    def actives(self):
        """Annonces visibles publiquement : publiées et non expirées (30 jours, SRS §3.3)."""
        from django.conf import settings as reglages
        from django.utils import timezone
        import datetime

        limite = timezone.now() - datetime.timedelta(days=reglages.ANNONCE_DUREE_JOURS)
        return self.filter(statut=Annonce.Statut.PUBLIEE, date_publication__gte=limite)


class Annonce(models.Model):
    """Annonce publiée par un vendeur — SRS §3.3, décisions Q4, Q8, Q9, Q10."""

    class Devise(models.TextChoices):
        USD = "USD", "$ (dollars américains)"
        CDF = "CDF", "FC (francs congolais)"

    class Contact(models.TextChoices):
        TELEPHONE = "telephone", "Numéro affiché sur l'annonce"
        MESSAGERIE = "messagerie", "Messagerie interne uniquement"

    class Statut(models.TextChoices):
        PUBLIEE = "publiee", "Publiée"
        RETIREE = "retiree", "Retirée par le vendeur"
        SUSPENDUE = "suspendue", "Suspendue par la modération"

    vendeur = models.ForeignKey(
        "comptes.Utilisateur", on_delete=models.CASCADE, related_name="annonces"
    )
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="annonces")
    commune = models.ForeignKey("geo.Commune", on_delete=models.PROTECT, related_name="annonces")
    titre = models.CharField("titre", max_length=120)
    slug = models.SlugField(max_length=140, blank=True)
    description = models.TextField("description")
    # Prix facultatif (décision Q8) : soit montant + devise, soit « à discuter ».
    prix = models.DecimalField("prix", max_digits=14, decimal_places=2, null=True, blank=True)
    devise = models.CharField("devise", max_length=3, choices=Devise.choices, blank=True)
    prix_a_discuter = models.BooleanField("prix à discuter", default=False)
    contact = models.CharField(
        "mode de contact", max_length=12, choices=Contact.choices, default=Contact.TELEPHONE
    )
    # Valeurs des champs spécifiques de la catégorie : {code: valeur}.
    attributs = models.JSONField(default=dict, blank=True)
    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.PUBLIEE)
    date_creation = models.DateTimeField(auto_now_add=True)
    # Date de publication ou de dernier renouvellement : sert au tri,
    # à l'expiration (30 jours) et à la limite de renouvellement (Q10).
    date_publication = models.DateTimeField(db_index=True)
    # Réservé pour la future mise en avant payante (SRS §8) — inactif dans le MVP.
    premium_jusqu_au = models.DateTimeField(null=True, blank=True, editable=False)

    objects = AnnonceQuerySet.as_manager()

    class Meta:
        verbose_name = "annonce"
        ordering = ["-date_publication"]

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("annonces:detail", kwargs={"pk": self.pk, "slug": self.slug or "annonce"})

    @property
    def expire_le(self):
        import datetime

        from django.conf import settings as reglages

        return self.date_publication + datetime.timedelta(days=reglages.ANNONCE_DUREE_JOURS)

    @property
    def est_expiree(self):
        from django.utils import timezone

        return timezone.now() >= self.expire_le

    @property
    def peut_renouveler(self):
        """Décision Q10 : au plus un renouvellement tous les 7 jours (configurable)."""
        import datetime

        from django.conf import settings as reglages
        from django.utils import timezone

        if self.statut != self.Statut.PUBLIEE:
            return False
        anciennete = timezone.now() - self.date_publication
        return anciennete >= datetime.timedelta(days=reglages.ANNONCE_RENOUVELLEMENT_JOURS)

    def champs_renseignes(self):
        """Paires (définition de champ, valeur) pour l'affichage du détail."""
        resultat = []
        for champ in self.categorie.champs.filter(actif=True):
            valeur = self.attributs.get(champ.code)
            if valeur not in (None, ""):
                resultat.append((champ, valeur))
        return resultat


class Photo(models.Model):
    """Photo d'annonce, redimensionnée à l'envoi (SRS §5.2) :
    - image : version d'affichage (côté max configurable, JPEG) ;
    - vignette : version légère pour les listes, cruciale en 3G."""

    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="annonces/%Y/%m/")
    vignette = models.ImageField(upload_to="annonces/%Y/%m/vignettes/", blank=True)
    ordre = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = "photo"
        ordering = ["ordre"]

    def save(self, *args, **kwargs):
        if not self.pk and self.image and not self.vignette:
            self._traiter_image()
        super().save(*args, **kwargs)

    def _traiter_image(self):
        import io
        from pathlib import Path

        from django.conf import settings as reglages
        from django.core.files.base import ContentFile
        from PIL import Image, ImageOps

        originale = Image.open(self.image)
        originale = ImageOps.exif_transpose(originale).convert("RGB")
        racine = Path(self.image.name).stem[:60] or "photo"

        def en_jpeg(cote_max):
            copie = originale.copy()
            copie.thumbnail((cote_max, cote_max))
            tampon = io.BytesIO()
            copie.save(tampon, format="JPEG", quality=82, optimize=True)
            return ContentFile(tampon.getvalue())

        self.image = en_jpeg(reglages.PHOTO_COTE_MAX)
        self.image.name = f"{racine}.jpg"
        self.vignette = en_jpeg(reglages.PHOTO_VIGNETTE_MAX)
        self.vignette.name = f"{racine}-min.jpg"


class ClicAffichageNumero(models.Model):
    """Journal des clics « Afficher le numéro » — décisions Q1 et Q9.

    Sert de preuve de contact pour le droit de laisser un avis, et de
    statistique pour le vendeur.
    """

    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name="clics_numero")
    utilisateur = models.ForeignKey(
        "comptes.Utilisateur", on_delete=models.CASCADE, related_name="clics_numero"
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "clic « afficher le numéro »"
        verbose_name_plural = "clics « afficher le numéro »"
        constraints = [
            models.UniqueConstraint(fields=["annonce", "utilisateur"], name="un_clic_par_annonce_et_utilisateur"),
        ]
