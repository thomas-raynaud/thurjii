from django.db import models
from datetime import date
from django.contrib.gis.db import models as modelsPG

class Cepage(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nom

class Taille(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nom

class Pliage(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nom

class Parcelle(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    cepage = models.ForeignKey(Cepage, on_delete=models.RESTRICT)
    taille = models.ForeignKey(Taille, on_delete=models.RESTRICT)
    pliage = models.ForeignKey(Pliage, on_delete=models.RESTRICT)
    region = modelsPG.PolygonField() #srid=3857
    """
    image = models.ImageField(upload_to="parcelles/")
    taille_img_x = models.DecimalField(max_digits=6, decimal_places=2)
    taille_img_y = models.DecimalField(max_digits=6, decimal_places=2)
    """
    def __str__(self):
        return self.nom

class Rang(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE)
    p0 = modelsPG.PointField()
    p1 = modelsPG.PointField()
    def __str__(self):
        return "Rang " + self.id + " de la parcelle " + self.parcelle.nom

class Saison(models.Model):
    annee = models.IntegerField(unique=True)
    terminee = models.BooleanField(default=False)
    def __str__(self):
        return "Saison " + self.annee + (" (terminée)" if self.terminee else "")

class EtatRang(models.Model):
    rang = models.ForeignKey(Rang, on_delete=models.CASCADE)
    saison = models.ForeignKey(Saison, on_delete=models.CASCADE)
    remaillage = models.BooleanField(default=False)
    taille = models.BooleanField(default=False)
    pliage = models.BooleanField(default=False)
    mondage = models.BooleanField(default=False)
    mondage_2 = models.BooleanField(default=False)
    mouchage = models.BooleanField(default=False)
    relevage = models.BooleanField(default=False)
    relevage_2 = models.BooleanField(default=False)
    effeuillage = models.BooleanField(default=False)
    vendange = models.BooleanField(default=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['rang', 'saison'],
                name='unique_rang_saison_combinaison'
            )
        ]
    def __str__(self):
        return self.rang + " - " + self.saison

class TypeReparation(models.Model):
    nom = models.CharField(max_length=50)
    def __str__(self):
        return self.nom

class Reparation(models.Model):
    type_reparation = models.ForeignKey(TypeReparation, on_delete=models.RESTRICT)
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE)
    rang = models.ForeignKey(Rang, on_delete=models.CASCADE)
    position = models.DecimalField(max_digits=3, decimal_places=3)
    date_accident = models.DateField(default=date.today)
    realisee = models.BooleanField(default=False)
    def __str__(self):
        return  (
            "Reparation de " + self.rang + " - type : " + self.type_reparation
            + (" (réalisée)" if self.realisee else "")
            + " - date : " + self.date_accident
        )

class TypeTache(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nom

class Log(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE)
    type_tache = models.ForeignKey(TypeTache, on_delete=models.RESTRICT)
    nb_heures = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    commentaire = models.TextField(max_length=300)
    def __str__(self):
        return (
            "Log parcelle " + self.parcelle.nom + " - "
            + self.type_tache + " - " + self.date
        )

class Rappel(models.Model):
    nom = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    fait = models.BooleanField(default=0)
    def __str__(self):
        return (
            self.nom + " - " + self.date + (" (fait)" if self.fait else "")
        )