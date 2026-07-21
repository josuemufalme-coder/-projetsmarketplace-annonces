from django.contrib import admin

from .models import Avis


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ("auteur", "vendeur", "note", "date")
    list_filter = ("note",)
    search_fields = ("auteur__email", "vendeur__email", "commentaire")
