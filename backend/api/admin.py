from django.contrib import admin

from .models import (
    Cepage, Taille, Pliage, Parcelle, Rang,
    Saison, EtatRang, TypeReparation, Reparation, TypeTache, Log, Rappel
)

admin.site.register(Cepage)
admin.site.register(Taille)
admin.site.register(Pliage)
admin.site.register(Parcelle)
admin.site.register(Rang)
admin.site.register(Saison)
admin.site.register(EtatRang)
admin.site.register(TypeReparation)
admin.site.register(Reparation)
admin.site.register(TypeTache)
admin.site.register(Log)
admin.site.register(Rappel)