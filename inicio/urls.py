from django.conf.urls import url

from inicio.views import InicioView

urlpatterns = [
    url(r'^/$', InicioView.as_view(), name="Inicio")

]