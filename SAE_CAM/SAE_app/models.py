from django.db import models

class Capteur(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    nom = models.CharField(max_length=100, unique=True)
    piece = models.CharField(max_length=100)
    emplacement = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nom} ({self.id})"

class Data(models.Model):
    id = models.ForeignKey(id,on_delete=models.CASCADE,db_column='id')
    date_heure = models.DateTimeField('date heure')

    def __str__(self):
        return f"{self.id}"