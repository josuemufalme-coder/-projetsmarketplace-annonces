from django.urls import path

from . import views

app_name = "annonces"

urlpatterns = [
    path("annonces/", views.liste, name="liste"),
    path("publier/", views.choisir_categorie, name="publier"),
    path("publier/<slug:slug>/", views.publier, name="publier_categorie"),
    path("mes-annonces/", views.mes_annonces, name="mes_annonces"),
    # Les actions (segments fixes) doivent précéder la page de détail,
    # dont le motif <slug> capturerait sinon « numero », « renouveler »…
    path("annonce/<int:pk>/numero/", views.afficher_numero, name="numero"),
    path("annonce/<int:pk>/renouveler/", views.renouveler, name="renouveler"),
    path("annonce/<int:pk>/retirer/", views.retirer, name="retirer"),
    path("annonce/<int:pk>/<slug:slug>/", views.detail, name="detail"),
]
