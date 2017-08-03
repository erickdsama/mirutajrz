from django.conf.urls import url

from inicio.views import InicioView, ProcesaArchivo, GetRuta

urlpatterns = [
    url(r'^$', InicioView.as_view(), name="Inicio"),
    url(r'^procesa_archivo/$', ProcesaArchivo.as_view(), name="Procesa"),
    url(r'^api/getruta/$', GetRuta.as_view(), name="APIRuta"),

]