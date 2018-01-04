from django import forms
from django.forms import Form

from backprocess.models import Ruta


class FormUpload(Form):
    kml = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
