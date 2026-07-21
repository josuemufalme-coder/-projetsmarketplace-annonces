from django.urls import path

from . import views

app_name = "messagerie"

urlpatterns = [
    path("messages/", views.boite, name="boite"),
    path("messages/<int:pk>/", views.conversation, name="conversation"),
    path("messages/contacter/<int:pk>/", views.contacter, name="contacter"),
]
