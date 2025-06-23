from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from . import models

class capteurForm(forms.ModelForm):
    class Meta:
        model = models.Capteur
        fields = ('id', 'nom', 'piece', 'emplacement')
        labels = {
            'id': _('Id'),
            'nom': _("Nom"),
            'piece': _("Piece"),
            'emplacement': _("Emplacement"),
        }

class dataForm(forms.ModelForm):
    class Meta:
        model = models.Data
        fields = ('id_data', 'date_heure')
        labels = {
            'id_data': _('Id'),
            'date_heure': _("Date et Heure"),
        }