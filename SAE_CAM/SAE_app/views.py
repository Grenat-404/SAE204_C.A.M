import csv
from django.shortcuts import render
from django.http import HttpResponse
from .models import Data, Capteur

def index(request):
    pieces = ['sejour', 'chambre1']
    latest_by_piece = {}
    chart_data = {}

    for piece in pieces:
        qs = (Data.objects.select_related('id_data').filter(id_data__piece=piece).order_by('-date_heure'))
        latest_by_piece[piece] = qs.first()
        chart_data[piece] = list(qs[:20])[::-1]

    return render(request, 'index.html', {'latest_by_piece': latest_by_piece,'chart_data': chart_data,})

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
    data_list = Data.objects.select_related('id').all()
    return render(request, 'affiche.html', {'data_list': data_list})