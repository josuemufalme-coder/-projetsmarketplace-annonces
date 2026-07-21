from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

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
    # Réinitialisation de mot de passe par e-mail (vues Django standard).
    path(
        "mdp-oublie/",
        auth_views.PasswordResetView.as_view(
            template_name="comptes/mdp_oublie.html",
            email_template_name="comptes/mdp_email.txt",
            subject_template_name="comptes/mdp_sujet.txt",
            success_url=reverse_lazy("comptes:mdp_envoye"),
        ),
        name="mdp_oublie",
    ),
    path(
        "mdp-envoye/",
        auth_views.PasswordResetDoneView.as_view(template_name="comptes/mdp_envoye.html"),
        name="mdp_envoye",
    ),
    path(
        "mdp-nouveau/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="comptes/mdp_nouveau.html",
            success_url=reverse_lazy("comptes:mdp_termine"),
        ),
        name="mdp_nouveau",
    ),
    path(
        "mdp-termine/",
        auth_views.PasswordResetCompleteView.as_view(template_name="comptes/mdp_termine.html"),
        name="mdp_termine",
    ),
]
