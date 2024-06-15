from django.urls import path

from . import views

urlpatterns = [
    path("parcelles", views.parcelles, name="parcelles"),
]