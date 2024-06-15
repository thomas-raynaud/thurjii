from django.db import models

class Cepage(models.Model):
    nom = models.CharField(max_length=50)

class Taille(models.Model):
    nom = models.CharField(max_length=50)

class Parcelle(models.Model):
    nom = models.CharField(max_length=50)

class SousParcelle(models.Model):
    nom = models.CharField(max_length=50)
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE)
    cepage = models.ForeignKey(Cepage, on_delete=models.SET_NULL)
    taille = models.ForeignKey(Taille, on_delete=models.SET_NULL)
    densite = models.DecimalField()
    superficie = models.DecimalField()

class Rang(models.Model):
    sous_parcelle = models.ForeignKey(SousParcelle, on_delete=models.CASCADE)
    location = models.CharField(100)

class TypeReparation(models.Model):
    nom = models.CharField()

class Reparation(models.Model):
    rang = models.ForeignKey(Rang, on_delete=models.CASCADE)
    position = models.DecimalField()
    type_reparation = models.ForeignKey(TypeReparation, on_delete=models.SET_NULL)
    date_accident = models.DateField()
    realise = models.BooleanField(default=False)

class TypeTache(models.Model):
    nom = models.CharField(max_length=50)

class Log(models.Model):
    sous_parcelle = models.ForeignKey(SousParcelle, on_delete=models.CASCADE)
    type_tache = models.ForeignKey(TypeTache, on_delete=models.SET_NULL)
    nb_heures = models.DecimalField()
    date = models.DateField()
    commentaire = models.CharField(max_length=200)

class Rappel(models.Model):
    nom = models.CharField(max_length=100)
    date = models.DateField()
    realise = models.BooleanField(default=0)
