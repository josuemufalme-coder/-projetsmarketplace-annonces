from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "comptes"

urlpatterns = [
    path("inscription/", views.inscription, name="inscription"),
    path(
        "connexion/",
        auth_views.LoginView.as_view(template_name="comptes/connexion.html"),
        name="connexion",
    ),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="deconnexion"),
    path("profil/", views.profil, name="profil"),
    path("vendeur/<int:pk>/", views.vendeur, name="vendeur"),
]
