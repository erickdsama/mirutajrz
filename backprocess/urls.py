from django.conf.urls import url

from backprocess.views import SyncTrack
from inicio.views import InicioView, ProcesaArchivo, GetRuta, UploadFile, SteperByRoutes

urlpatterns = [
    url(r'^api/sync/$', SyncTrack, name="Sync"),
]