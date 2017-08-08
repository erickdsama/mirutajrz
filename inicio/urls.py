from django.conf.urls import url

from inicio.views import InicioView, ProcesaArchivo, GetRuta, UploadFile

urlpatterns = [
    url(r'^$', InicioView.as_view(), name="Inicio"),
    url(r'^upload/$', UploadFile.as_view(), name="Upload"),
    url(r'^procesa_archivo/$', ProcesaArchivo.as_view(), name="Procesa"),
    url(r'^api/getruta/$', GetRuta.as_view(), name="APIRuta"),
]