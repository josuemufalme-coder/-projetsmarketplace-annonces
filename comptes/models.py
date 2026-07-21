"""Comptes utilisateurs — SRS §3.1, décisions Q3 et R1.

Connexion par e-mail + mot de passe (R1). Pas de vérification SMS dans le
MVP (Q3) : le téléphone est déclaratif et le statut de vérification est
réservé pour la version future. La commune du profil vient du référentiel
géographique.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UtilisateurManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire.")
        utilisateur = self.model(email=self.normalize_email(email), **extra)
        utilisateur.set_password(password)
        utilisateur.save(using=self._db)
        return utilisateur

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra)


class Utilisateur(AbstractUser):
    class Verification(models.TextChoices):
        NON_VERIFIE = "non_verifie", "Non vérifié"
        VERIFIE_SMS = "verifie_sms", "Vérifié par SMS"

    username = None
    first_name = None
    last_name = None

    email = models.EmailField(_("adresse e-mail"), unique=True)
    nom_affichage = models.CharField(_("nom affiché"), max_length=60)
    telephone = models.CharField(
        _("téléphone"),
        max_length=20,
        blank=True,
        help_text=_("Affiché sur vos annonces uniquement si vous choisissez le mode « numéro affiché »."),
    )
    commune = models.ForeignKey(
        "geo.Commune",
        verbose_name=_("commune"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="habitants",
    )
    verification = models.CharField(
        "vérification",
        max_length=20,
        choices=Verification.choices,
        default=Verification.NON_VERIFIE,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nom_affichage"]

    objects = UtilisateurManager()

    class Meta:
        verbose_name = "utilisateur"

    def __str__(self):
        return self.nom_affichage or self.email
