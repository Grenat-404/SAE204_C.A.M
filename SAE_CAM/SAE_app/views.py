import csv
from django.shortcuts import render
from django.http import HttpResponse
from .models import Data, Capteur
from django.shortcuts import redirect
from django.urls import reverse


def index(request):
    pieces = ['sejour', 'chambre1']
    latest_by_piece = {}
    chart_data = {}

    for piece in pieces:
        qs = (Data.objects.select_related('id_data').filter(id_data__piece=piece).order_by('-date_heure'))
        latest_by_piece[piece] = qs.first()
        chart_data[piece] = list(qs[:50])[::-1]

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


#def Affiche(request):
#    data_list = Data.objects.select_related('id').all()
#    return render(request, 'affiche.html', {'data_list': data_list})

def Affiche(request):
    qs = Data.objects.select_related('id_data').all()
    selected_nom = request.GET.get('nom')
    search_id = request.GET.get('search_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    selected_emplacement = request.GET.get('emplacement')
    selected_piece = request.GET.get('piece')

    if search_id:
        qs = qs.filter(id_data__id=search_id)
    if selected_nom:
        qs = qs.filter(id_data__nom=selected_nom)
    if date_from:
        qs = qs.filter(date_heure__date__gte=date_from)
    if date_to:
        qs = qs.filter(date_heure__date__lte=date_to)
    if selected_emplacement:
        qs = qs.filter(id_data__emplacement=selected_emplacement)
    if selected_piece:
        qs = qs.filter(id_data__piece=selected_piece)

    qs = qs.order_by('-date_heure')

    capteurs = Capteur.objects.all()
    emplacements = Data.objects.values_list('id_data__emplacement', flat=True).distinct()
    pieces = Data.objects.values_list('id_data__piece', flat=True).distinct()
    noms = Data.objects.values_list('id_data__nom', flat=True).distinct()

    return render(request, 'BD.html', {
        'data_list': qs,
        'capteurs': capteurs,
        'noms': noms,
        'selected_nom': selected_nom or '',
        'emplacements': emplacements,
        'selected_emplacement': selected_emplacement or '',
        'pieces': pieces,
        'selected_piece': selected_piece or '',
    })

def export_csv(request):
    qs = Data.objects.select_related('id_data').all()

    search_id = request.GET.get('search_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    emplacement = request.GET.get('emplacement')
    piece = request.GET.get('piece')
    nom = request.GET.get('nom')

    if search_id:
        qs = qs.filter(id_data__id=search_id)
    if date_from:
        qs = qs.filter(date_heure__date__gte=date_from)
    if date_to:
        qs = qs.filter(date_heure__date__lte=date_to)
    if emplacement:
        qs = qs.filter(id_data__emplacement=emplacement)
    if piece:
        qs = qs.filter(id_data__piece=piece)
    if nom:
        qs = qs.filter(id_data__nom=nom)

    qs = qs.order_by('-date_heure')

    # 3) génération du CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export_capteurs.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Capteur ID', 'Nom', 'Pièce', 'Emplacement', 'Date / Heure', 'Température (°C)'
    ])
    for data in qs:
        cap = data.id_data
        writer.writerow([
            cap.id,
            cap.nom,
            cap.piece,
            cap.emplacement,
            data.date_heure.strftime('%Y-%m-%d %H:%M:%S'),
            data.temp,
        ])
    return response

def rename_capteur(request):
    if request.method == 'POST':
        capteur_id = request.POST.get('capteur_id')
        new_name   = request.POST.get('new_name')
        try:
            cap = Capteur.objects.get(pk=capteur_id)
            cap.nom = new_name
            cap.save()
        except Capteur.DoesNotExist:
            pass
    return redirect(request.META.get('HTTP_REFERER', reverse('index')))
