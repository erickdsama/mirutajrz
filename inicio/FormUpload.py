from django import forms

from backprocess.models import Ruta


class FormUpload(forms.ModelForm):
    kml = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
