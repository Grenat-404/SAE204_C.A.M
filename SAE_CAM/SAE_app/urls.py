from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('export/', views.Update, name='export'),
    path('BD/', views.Affiche, name='BD'),
]