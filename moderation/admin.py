"""File de revue de la modération — SRS §3.7/§3.8.

Les signalements et les marques anti-spam arrivent « En attente » ; les
actions permettent de rejeter, ou de suspendre / republier l'annonce.
Chaque action est journalisée par l'historique d'administration.
"""

from django.contrib import admin

from annonces.models import Annonce

from .models import MarqueAntiSpam, MotifFrauduleux, MotifSignalement, Signalement


@admin.register(MotifSignalement)
class MotifSignalementAdmin(admin.ModelAdmin):
    list_display = ("nom_fr", "code", "ordre", "actif")
    list_editable = ("ordre", "actif")
    prepopulated_fields = {"code": ("nom_fr",)}


@admin.register(MotifFrauduleux)
class MotifFrauduleuxAdmin(admin.ModelAdmin):
    list_display = ("expression", "actif")
    list_editable = ("actif",)


class ActionsFileDeRevue:
    """Actions communes aux signalements et aux marques anti-spam."""

    def _annonces(self, queryset):
        return Annonce.objects.filter(pk__in=queryset.values("annonce"))

    @admin.action(description="Rejeter (fausse alerte)")
    def rejeter(self, request, queryset):
        queryset.update(statut=self.STATUT_REJET)
        for objet in queryset:
            self.log_change(request, objet, "Rejeté (fausse alerte)")

    @admin.action(description="Suspendre l'annonce et marquer traité")
    def suspendre_annonce(self, request, queryset):
        self._annonces(queryset).update(statut=Annonce.Statut.SUSPENDUE)
        queryset.update(statut=self.STATUT_TRAITE)
        for objet in queryset:
            self.log_change(request, objet, "Annonce suspendue")

    @admin.action(description="Republier l'annonce et marquer traité")
    def republier_annonce(self, request, queryset):
        self._annonces(queryset).update(statut=Annonce.Statut.PUBLIEE)
        queryset.update(statut=self.STATUT_TRAITE)
        for objet in queryset:
            self.log_change(request, objet, "Annonce republiée")


@admin.register(Signalement)
class SignalementAdmin(ActionsFileDeRevue, admin.ModelAdmin):
    STATUT_REJET = Signalement.Statut.REJETE
    STATUT_TRAITE = Signalement.Statut.TRAITE

    list_display = ("annonce", "motif", "auteur", "date", "statut")
    list_filter = ("statut", "motif")
    search_fields = ("annonce__titre", "commentaire")
    actions = ["rejeter", "suspendre_annonce", "republier_annonce"]
    readonly_fields = ("annonce", "auteur", "motif", "commentaire", "date")


@admin.register(MarqueAntiSpam)
class MarqueAntiSpamAdmin(ActionsFileDeRevue, admin.ModelAdmin):
    STATUT_REJET = MarqueAntiSpam.Statut.REJETEE
    STATUT_TRAITE = MarqueAntiSpam.Statut.TRAITEE

    list_display = ("annonce", "regle", "detail", "date", "statut")
    list_filter = ("statut", "regle")
    search_fields = ("annonce__titre", "detail")
    actions = ["rejeter", "suspendre_annonce", "republier_annonce"]
    readonly_fields = ("annonce", "regle", "detail", "date")
