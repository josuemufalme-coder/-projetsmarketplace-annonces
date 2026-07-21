from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "nom_affichage", "commune", "verification", "is_active", "date_joined")
    list_filter = ("is_active", "verification", "is_staff")
    search_fields = ("email", "nom_affichage", "telephone")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profil", {"fields": ("nom_affichage", "telephone", "commune", "verification")}),
        ("Droits", {"fields": ("is_active", "is_staff", "is_superuser", "groups")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "nom_affichage", "password1", "password2")}),
    )
