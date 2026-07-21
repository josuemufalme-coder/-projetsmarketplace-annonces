from django.contrib import admin

from .models import Commune, Ville


class CommuneInline(admin.TabularInline):
    model = Commune
    extra = 0
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display = ("nom", "actif", "nombre_de_communes")
    list_filter = ("actif",)
    search_fields = ("nom",)
    prepopulated_fields = {"slug": ("nom",)}
    inlines = [CommuneInline]

    @admin.display(description="communes")
    def nombre_de_communes(self, obj):
        return obj.communes.count()


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ("nom", "ville", "actif")
    list_filter = ("ville", "actif")
    search_fields = ("nom",)
    prepopulated_fields = {"slug": ("nom",)}
