from django.contrib import admin

from .models import Annonce, Categorie, ChampCategorie, ClicAffichageNumero, Photo


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


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0


@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ("titre", "vendeur", "categorie", "commune", "prix", "devise", "statut", "date_publication")
    list_filter = ("statut", "categorie", "commune", "devise", "contact")
    search_fields = ("titre", "description", "vendeur__email")
    date_hierarchy = "date_publication"
    inlines = [PhotoInline]
    actions = ["suspendre", "republier"]

    @admin.action(description="Suspendre les annonces sélectionnées")
    def suspendre(self, request, queryset):
        queryset.update(statut=Annonce.Statut.SUSPENDUE)

    @admin.action(description="Republier les annonces sélectionnées")
    def republier(self, request, queryset):
        queryset.update(statut=Annonce.Statut.PUBLIEE)


@admin.register(ClicAffichageNumero)
class ClicAffichageNumeroAdmin(admin.ModelAdmin):
    list_display = ("annonce", "utilisateur", "date")
    date_hierarchy = "date"
