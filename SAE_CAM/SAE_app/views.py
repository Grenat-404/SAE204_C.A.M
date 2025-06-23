import csv
from django.shortcuts import render
from django.http import HttpResponse
from .models import Data, Capteur

def index(request):
    return render(request, 'index.html')

def Update(request):


def Affiche(request):
