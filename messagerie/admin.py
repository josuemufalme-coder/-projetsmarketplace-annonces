from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("expediteur", "texte", "date", "lu")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("annonce", "acheteur", "date_creation")
    search_fields = ("annonce__titre", "acheteur__email")
    inlines = [MessageInline]
