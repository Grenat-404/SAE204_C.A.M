import csv
from django.shortcuts import render
from django.http import HttpResponse
from .models import Data, Capteur

def index(request):
    latest_data = Data.objects.select_related('id_data').order_by('-date_heure')[:2]
    return render(request, 'index.html', {'latest_data': latest_data})

def Update(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data_capteurs.csv"'
    writer = csv.writer(response)
    writer.writerow(['Capteur ID', 'Nom', 'Piece', 'Emplacement', 'Date et Heure'])
    for data in Data.objects.select_related('id').all():
        capteur = data.id
        writer.writerow([
            capteur.id,
            capteur.nom,
            capteur.piece,
            capteur.emplacement,
            data.date_heure,
            data.temp,
        ])
    return response


def Affiche(request):
    # Retrieve all Data entries with their related Capteur
    data_list = Data.objects.select_related('id').all()
    # Render in template 'affiche.html'
    return render(request, 'affiche.html', {'data_list': data_list})