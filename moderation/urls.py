from django.urls import path

from . import views

app_name = "moderation"

urlpatterns = [
    path("signaler/<int:pk>/", views.signaler, name="signaler"),
]
