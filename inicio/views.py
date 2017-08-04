# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.db.models.functions import Distance as qDistance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import Distance
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.generic.base import View
from rest_framework.response import Response
from rest_framework.views import APIView

from ProcessKMLFile import ProcessKMLFile
from backprocess.models import Ruta, RutaCoordenda
from mirutajrz.settings import BASE_DIR


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

        ruta = None
        for coordendada in coordendadas2:
            # print "salgo", coordendada.distance, coordendada
            ruta = coordendada.ruta

        return render(request, self.template_name, context={"ruta":ruta})


class ProcesaArchivo(View, LoginRequiredMixin):

    def get(self, request):
        #obtener todas las rutas
        rutas = Ruta.objects.all()
        RutaCoordenda.objects.all().delete()
        for ruta in rutas:
            kml_file =  os.path.join(BASE_DIR+"/media/", str(ruta.kml))
            print kml_file
            kml = ProcessKMLFile(kml_file)
            route_obj = kml.file_to_objet()
            coords = route_obj.get("coordinates")

            for coord in coords:
                split_coord = coord.split(",")
                x = split_coord[0]
                y = split_coord[1]
                z = split_coord[2]
                point = GEOSGeometry("POINT({0} {1})".format(x, y))
                RutaCoordenda.objects.create(ruta=ruta, coordenadas=point)
            # soriana henequen 31.6482147,-106.3911803
            # smart libramiento 31.627863,-106.354794


        return JsonResponse(data=[],safe=False)


class GetRuta(APIView):

    def post(self, request):
        data_post = request.data
        lat_in =  data_post.get("lat_in") #y
        lon_in =  data_post.get("lon_in") #x
        lat_go =  data_post.get("lat_go") #y
        lon_go =  data_post.get("lon_go") #x
        print "POINT({} {})".format(lon_in, lat_in)
        point_of_user = GEOSGeometry("POINT({} {})".format(lon_in, lat_in))
        point_to_go = GEOSGeometry("POINT({} {})".format(lon_go, lat_go))
        max_distance = 500  # m

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

        ruta = None
        rutas_to_send = []
        for coordendada in coordendadas2:
            print "salgo", coordendada.distance, coordendada
            obj = {}
            obj["id"] = coordendada.ruta.id
            obj["nombre"] = coordendada.ruta.nombre
            obj["distance"] = str(coordendada.distance)
            obj["kml"] = str(coordendada.ruta.kml)
            rutas_to_send.append(obj)

        return Response(data=rutas_to_send, status=200)