from datetime import timezone
from django.db import models

class Capteur(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    nom = models.CharField(max_length=100, unique=True)
    piece = models.CharField(max_length=100)
    emplacement = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nom} ({self.id})"

class Data(models.Model):
    id_data = models.ForeignKey(Capteur, on_delete=models.CASCADE,null=True, blank=True)
    date_heure = models.DateTimeField()

    def __str__(self):
        return f"{self.id_data}"