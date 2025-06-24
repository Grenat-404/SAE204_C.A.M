from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('export/', views.export_csv, name='export'),
    path('BD/', views.Affiche, name='BD'),
    path('rename/', views.rename_capteur, name='rename'),
    path('rename-emplacement/', views.rename_emplacement, name='rename_emplacement'),
]