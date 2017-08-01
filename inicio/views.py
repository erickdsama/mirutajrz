# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic.base import View

from ProcessKMLFile import ProcessKMLFile
from backprocess.models import Ruta, RutaCoordenda


class InicioView(View):
    template_name = "inicio.html"

    def get(self, request):
        # todo change this
        kml_file = "/Users/mariomontes/file.kml"
        kml = ProcessKMLFile(kml_file)
        route_obj = kml.file_to_objet()

        ruta = Ruta.objects.create(nombre=route_obj.get("name"), color=route_obj.get("colorLine"), kml="")

        coords = route_obj.get("coordinates")

        for coord in coords:
            ruta_coord = RutaCoordenda.objects.create(ruta=ruta, coordenadas=coord)
            print type(coord), ruta_coord
        return render(request, self.template_name)
