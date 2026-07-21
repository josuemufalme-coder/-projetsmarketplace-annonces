from django.urls import path

from . import views

app_name = "avis"

urlpatterns = [
    path("vendeur/<int:pk>/avis/", views.laisser_avis, name="laisser"),
]
