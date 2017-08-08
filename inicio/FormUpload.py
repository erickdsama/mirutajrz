from django import forms

from backprocess.models import Ruta


class FormUpload(forms.ModelForm):
    class Meta:
        model = Ruta
        fields = ("kml",)