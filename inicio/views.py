# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.db.models.functions import Distance as qDistance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.linestring import LineString
from django.contrib.gis.measure import Distance
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.generic.base import View
from pykml import parser
from rest_framework.response import Response
from rest_framework.views import APIView

from ProcessKMLFile import ProcessKMLFile
from backprocess.models import Ruta, RutaCoordenda, NodosRutas
from inicio.FormUpload import FormUpload
from mirutajrz.settings import BASE_DIR


class InicioView(View):
    template_name = "inicio.html"

    def get(self, request):
        # soriana henequen 31.6482147,-106.3911803

        point_of_user = GEOSGeometry("POINT({} {})".format(-106.38932704925537, 31.64799289324259))
        point_to_go = GEOSGeometry("POINT({} {})".format(-106.39343619346619, 31.64873268974223))

        rutas_salida = Ruta.objects.filter(puntos__distance_lte=(point_of_user, Distance(chain=100)))
        rutas_salida = rutas_salida.filter(puntos__distance_lte=(point_to_go, Distance(chain=100)))

        print "r", rutas_salida

        rutas_llegada = GEOSGeometry("POINT({} {})".format(-106.354794, 31.627863))
        # max_distance = 250  # m
        #
        # coordendadas = RutaCoordenda.objects.filter(
        #     coordenadas__distance_lt=(
        #         point_of_user,
        #         Distance(m=max_distance)
        #     ),
        # ).annotate(distance=qDistance('coordenadas', point_of_user)).distinct("ruta")
        #
        # ids = []
        # for coordendada in coordendadas:
        #     print coordendada
        #     ids.append(coordendada.ruta_id)
        #
        # coordendadas2 = RutaCoordenda.objects.filter(coordenadas__distance_lt=(
        #     point_to_go,
        #     Distance(m=max_distance)
        # ),
        #     ruta__id__in=ids
        # ).annotate(distance=qDistance('coordenadas', point_to_go)).distinct("ruta")


        ruta1 = Ruta.objects.get(pk=42)
        print rutas_salida
        print Ruta.objects.filter(puntos__crosses=rutas_salida[0].puntos)

        ruta = None
        # for coordendada in coordendadas2:
        #     # print "salgo", coordendada.distance, coordendada
        #     ruta = coordendada.ruta

        return render(request, self.template_name, context={"ruta": ruta})


class UploadFile(View):
    template_name = "upload.html"

    def get(self, request):
        form = FormUpload()
        return render(request, self.template_name, context={
            "form": form
        })

    def post(self, request):
        form = FormUpload(request.POST, request.FILES)
        if form.is_valid():
            print "valido"
            file = request.FILES['kml']
            # self.handle_uploaded_file(request.FILES['kml'])
            kml_process = ProcessKMLFile(request.FILES['kml'])
            data_kml = kml_process.file_to_objet()

            ruta = form.save()
            ruta.nombre = data_kml.get("name", "")
            ruta.color = data_kml.get("colorLine", "")
            ruta.http_kml = ""

            lista_nodos = []
            lista = []
            for coord in data_kml.get("coordinates"):
                split_coord = coord.split(",")
                x = split_coord[0]
                y = split_coord[1]
                z = split_coord[2]
                point = GEOSGeometry("POINT({0} {1})".format(x, y))
                lista.append(point)

                # checa los puntos actuales con las rutas ya guardadas
                # nodos = RutaCoordenda.objects.filter(
                #     coordenadas__distance_lt=(
                #         point,
                #         Distance(m=10)  # distance node
                #     ),
                # # ).annotate(distance=qDistance('coordenadas', point)).distinct("ruta")
                #
                #
                #
                #
                # for nodo in nodos:
                #     NodosRutas.objects.create(ruta_a = ruta, nodo=point, ruta_b=nodo.ruta)
                #
                # lista_nodos.append(nodos)
                # print "nodo", point, nodos
            ruta.puntos = LineString(lista)
            # RutaCoordenda.objects.create(ruta= ruta,coordenadas=lista[0], linea=ls)
            ruta.save()
            print lista_nodos


        else:
            print "no valido"
        return render(request, self.template_name, context={
            "form": form
        })

    def handle_uploaded_file(self, f):

        with open(os.path.join(BASE_DIR, "media/kml_files/") + str(f), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)


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
    max_distance = 100  # m

    def post(self, request):
        data_post = request.data
        lat_in = data_post.get("lat_in")  # y
        lon_in = data_post.get("lon_in")  # x
        lat_go = data_post.get("lat_go")  # y
        lon_go = data_post.get("lon_go")  # x
        print "POINT({} {})".format(lon_in, lat_in)
        point_of_user = GEOSGeometry("POINT({} {})".format(lon_in, lat_in))
        point_to_go = GEOSGeometry("POINT({} {})".format(lon_go, lat_go))

        rutas_salida = Ruta.objects.filter(puntos__distance_lte=(point_of_user, Distance(m=self.max_distance)))
        rutas_salida = rutas_salida.filter(puntos__distance_lte=(point_to_go, Distance(m=self.max_distance)))


        if len(rutas_salida) <= 0:
            rutas_salida = self.transborde(point_of_user, point_to_go)

        # coordendadas = RutaCoordenda.objects.filter(
        #     coordenadas__distance_lt=(
        #         point_of_user,
        #         Distance(m=self.max_distance)
        #     ),
        # ).annotate(distance=qDistance('coordenadas', point_of_user)).distinct("ruta")
        #
        # ids = []
        # for coordendada in coordendadas:
        #     print coordendada
        #     ids.append(coordendada.ruta_id)
        #
        # coordendadas2 = RutaCoordenda.objects.filter(coordenadas__distance_lt=(
        #     point_to_go,
        #     Distance(m=self.max_distance)
        # ),
        #     ruta__id__in=ids
        # ).annotate(distance=qDistance('coordenadas', point_to_go)).distinct("ruta")
        #
        # ruta = None
        rutas_to_send = []
        print rutas_salida
        for ruta in rutas_salida:
            print ruta.__dict__
            obj = {}
            obj["id"] = ruta.pk
            obj["nombre"] =ruta.nombre
            # obj["distance"] = str(coordendada.distance)
            obj["url"] = str(ruta.http_kml)
            obj["kml"] = str(ruta.kml)
            rutas_to_send.append(obj)

        if len(rutas_to_send) > 0:
            return Response(data=rutas_to_send, status=200)
        else:
            # try to get transboarding route
            rutas_to_send = self.transborde(point_of_user, point_to_go)
            return Response(data=rutas_to_send, status=200)



    def transborde(self, punto_partida, punto_final):
        rutas_salida = Ruta.objects.filter(puntos__distance_lte=(punto_partida, Distance(m=self.max_distance)))
        ruta_llegada = Ruta.objects.filter(puntos__distance_lte=(punto_final, Distance(m=self.max_distance)))
        llegadas_ids = ruta_llegada.values_list('id', flat=True)
        opciones = []
        for ruta in rutas_salida:
            print ruta
            cross =  Ruta.objects.filter(puntos__intersects=ruta.puntos, pk__in=llegadas_ids)
            opciones.append(ruta)
            opciones.append(cross[0])
        return opciones

    def checas_rutas(self, id, rutas):
        for ruta in rutas:
            if ruta.get("id") == id:
                return True
        return False
