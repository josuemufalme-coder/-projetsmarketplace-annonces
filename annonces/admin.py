from django.contrib import admin

from .models import Categorie, ChampCategorie


class ChampCategorieInline(admin.TabularInline):
    model = ChampCategorie
    extra = 0
    fields = ("ordre", "code", "nom_fr", "nom_ln", "nom_en", "type", "options", "unite", "obligatoire", "actif")


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nom_fr", "ordre", "photos_obligatoires", "actif", "nombre_de_champs")
    list_editable = ("ordre",)
    list_filter = ("actif", "photos_obligatoires")
    search_fields = ("nom_fr",)
    prepopulated_fields = {"slug": ("nom_fr",)}
    inlines = [ChampCategorieInline]

    @admin.display(description="champs spécifiques")
    def nombre_de_champs(self, obj):
        return obj.champs.count()
