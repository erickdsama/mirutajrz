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
from inicio.FormUpload import FormUpload
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

        return render(request, self.template_name, context={"ruta": ruta})

class UploadFile(View):
    template_name = "upload.html"

    def get(self, request):
        form = FormUpload()
        return render(request, self.template_name, context={
            "form":form
        })

    def post(self, request):
        form = FormUpload(request.POST, request.FILES)
        if form.is_valid():
            print "valido"
            print request.FILES['kml']
            ProcessKMLFile(request.FILES['kml'])
        else:
            print "no valido"
        return render(request, self.template_name, context={
            "form":form
        })



class ProcesaArchivo(View, LoginRequiredMixin):
    def get(self, request):
        # obtener todas las rutas
        rutas = Ruta.objects.all()
        RutaCoordenda.objects.all().delete()
        for ruta in rutas:
            kml_file = os.path.join(BASE_DIR + "/media/", str(ruta.kml))
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

        return JsonResponse(data=[], safe=False)


class GetRuta(APIView):
    def post(self, request):
        data_post = request.data
        lat_in = data_post.get("lat_in")  # y
        lon_in = data_post.get("lon_in")  # x
        lat_go = data_post.get("lat_go")  # y
        lon_go = data_post.get("lon_go")  # x
        print "POINT({} {})".format(lon_in, lat_in)
        point_of_user = GEOSGeometry("POINT({} {})".format(lon_in, lat_in))
        point_to_go = GEOSGeometry("POINT({} {})".format(lon_go, lat_go))
        max_distance = 200  # m

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
            obj["url"] = str(coordendada.ruta.http_kml)
            obj["kml"] = str(coordendada.ruta.kml)
            rutas_to_send.append(obj)

        if len(rutas_to_send) > 0:
            return Response(data=rutas_to_send, status=200)
        else:
            # try to get transboarding route
            rutas_to_send =  self.transborde(point_of_user, point_to_go)
            return Response(data=rutas_to_send, status=200)

    def transborde(self, punto_partida, punto_final):
        print "intentanto fijar ruta de transborde"

        # obtener rutas en punto de partida
        # punto_partida = GEOSGeometry("POINT({} {})".format(lon_in, lat_in))
        max_distance = 200  # m

        rutas_iniciales = RutaCoordenda.objects.filter(
            coordenadas__distance_lt=(
                punto_partida,
                Distance(m=max_distance)
            ),
        ).annotate(distance=qDistance('coordenadas', punto_partida)).distinct("ruta")

        # print rutas_iniciales

        # obtener rutas del punto deseado
        # punto_final = GEOSGeometry("POINT({} {})".format(lon_go, lat_go))
        max_distance = 200  # m

        rutas_finales = RutaCoordenda.objects.filter(
            coordenadas__distance_lt=(
                punto_final,
                Distance(m=max_distance)
            ),
        ).annotate(distance=qDistance('coordenadas', punto_final)).distinct("ruta")

        print rutas_iniciales
        print "*"*20
        print rutas_finales
        # script para buscar coordenadas coicidan

        #   obtener coordenadas de
        rutas = []
        for ruta_final in rutas_finales:
            print "obtiene las rutas de donde vamos"
            coordendas_ruta = RutaCoordenda.objects.filter(ruta=ruta_final.ruta)
            for coordenada in coordendas_ruta:
                for ruta_inicial in rutas_iniciales:
                    # print "buscando en las rutas iniciales", coordenada.coordenadas, ruta_inicial, ruta_final
                    buscador = RutaCoordenda.objects.filter(
                        coordenadas__distance_lt=(
                            coordenada.coordenadas,
                            Distance(m=50)
                        ),
                        ruta=ruta_inicial.ruta
                    ).annotate(distance=qDistance('coordenadas', punto_final)).distinct("ruta")
                    if len(buscador) > 0:
                        obj = {}
                        obj["id"] = ruta_final.ruta.id
                        obj["nombre"] = ruta_final.ruta.nombre
                        obj["distance"] = str(ruta_final.distance)
                        obj["url"] = str(ruta_final.ruta.http_kml)
                        obj["kml"] = str(ruta_final.ruta.kml)
                        obj2 = {}
                        obj2["id"] = ruta_inicial.ruta.id
                        obj2["nombre"] = ruta_inicial.ruta.nombre
                        obj2["distance"] = str(ruta_inicial.distance)
                        obj2["url"] = str(ruta_inicial.ruta.http_kml)
                        obj2["kml"] = str(ruta_inicial.ruta.kml)

                        if not self.checas_rutas(obj["id"], rutas):
                            rutas.append(obj)
                        if not self.checas_rutas(obj2["id"], rutas):
                            rutas.append(obj2)

                        # for ruta in rutas:
                        #     if
                        #     rutas.append(obj)
                        #
                        # if not any(ruta.id == obj2["id"] for ruta in rutas):
                        #     rutas.append(obj2)

        return rutas


    def checas_rutas(self, id, rutas):
        for ruta in rutas:
            if ruta.get("id") == id:
                return True
        return False

