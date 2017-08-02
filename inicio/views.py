# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import Distance
from django.db.models import Count
from django.db.models.aggregates import Min
from django.shortcuts import render
from django.views.generic.base import View

from ProcessKMLFile import ProcessKMLFile
from backprocess.models import Ruta, RutaCoordenda
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance as qDistance


class InicioView(View):
    template_name = "inicio.html"

    def get(self, request):

        point_of_user = GEOSGeometry("POINT({} {})".format(-106.3911803, 31.6482147))
        point_to_go = GEOSGeometry("POINT({} {})".format(-106.354794, 31.627863))
        max_distance = 250  # m

        coordendadas = RutaCoordenda.objects.filter(
            coordenadas__distance_lt=(
                point_of_user,
                Distance(m=max_distance)
            ),
        ).annotate(distance=qDistance('coordenadas', point_of_user)).distinct("ruta")

        ids = []
        for coordendada in coordendadas:
            print coordendada
            ids.append(coordendada.ruta_id)

        coordendadas2 = RutaCoordenda.objects.filter(coordenadas__distance_lt=(
            point_to_go,
            Distance(m=max_distance)
        ),
            ruta__id__in=ids
        ).annotate(distance=qDistance('coordenadas', point_to_go)).distinct("ruta")

        for coordendada in coordendadas2:
            print "salgo", coordendada.distance, coordendada

        return render(request, self.template_name)


class ProcessFiles(View):

    def get(self):
        # todo change this
        kml_file = "/Users/mariomontes/rutabosques.kml"
        kml = ProcessKMLFile(kml_file)
        route_obj = kml.file_to_objet()

        # ruta = Ruta.objects.create(nombre=route_obj.get("name"), color=route_obj.get("colorLine"), kml="")
        #
        # coords = route_obj.get("coordinates")
        #
        # for coord in coords:
        #     split_coord = coord.split(",")
        #     x = split_coord[0]
        #     y = split_coord[1]
        #     z = split_coord[2]
        #     point = GEOSGeometry("POINT({0} {1})".format(x, y))
        #     RutaCoordenda.objects.create(ruta=ruta, coordenadas=point)
        # soriana henequen 31.6482147,-106.3911803
        # smart libramiento 31.627863,-106.354794