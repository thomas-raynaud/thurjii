from django.db import models
from datetime import date

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
    loc_x = models.DecimalField(max_digits=8, decimal_places=5)
    loc_y = models.DecimalField(max_digits=8, decimal_places=5)
    loc_z = models.IntegerField()
    loc_r = models.DecimalField(max_digits=8, decimal_places=5)
    image = models.ImageField(upload_to="parcelles/")
    taille_img_x = models.DecimalField(max_digits=6, decimal_places=2)
    taille_img_y = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.nom

class SousParcelle(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE)
    cepage = models.ForeignKey(Cepage, on_delete=models.RESTRICT)
    taille = models.ForeignKey(Taille, on_delete=models.RESTRICT)
    pliage = models.ForeignKey(Pliage, on_delete=models.RESTRICT)
    densite = models.DecimalField(max_digits=3, decimal_places=2)
    image = models.ImageField(upload_to="parcelles/")
    taille_img_x = models.DecimalField(max_digits=6, decimal_places=2)
    taille_img_y = models.DecimalField(max_digits=6, decimal_places=2)
    loc_x = models.DecimalField(max_digits=8, decimal_places=5)
    loc_y = models.DecimalField(max_digits=8, decimal_places=5)
    loc_z = models.IntegerField()
    loc_r = models.DecimalField(max_digits=8, decimal_places=5)
    # Contient une liste de points sur l'image delimitant la sous-parcelle
    superficie = models.DecimalField(max_digits=5, decimal_places=2)
    perimetre = models.CharField(max_length=50)

    def __str__(self):
        return self.nom + " - sous-parcelle de " + self.parcelle.nom

class Rang(models.Model):
    sous_parcelle = models.ForeignKey(SousParcelle, on_delete=models.CASCADE)
    loc_img_x1 = models.DecimalField(max_digits=3, decimal_places=3)
    loc_img_x2 = models.DecimalField(max_digits=3, decimal_places=3)
    loc_img_y1 = models.DecimalField(max_digits=3, decimal_places=3)
    loc_img_y2 = models.DecimalField(max_digits=3, decimal_places=3)
    longueur = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return "Rang " + self.id + " de la sous-parcelle " + self.sous_parcelle.nom

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
    rang = models.ForeignKey(Rang, on_delete=models.CASCADE)
    position = models.DecimalField(max_digits=3, decimal_places=3)
    type_reparation = models.ForeignKey(TypeReparation, on_delete=models.RESTRICT)
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
    sous_parcelle = models.ForeignKey(SousParcelle, on_delete=models.CASCADE)
    type_tache = models.ForeignKey(TypeTache, on_delete=models.RESTRICT)
    nb_heures = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    commentaire = models.TextField(max_length=300)

    def __str__(self):
        return (
            "Log sous-parcelle " + self.sous_parcelle.nom + " - "
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