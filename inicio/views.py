# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import os
import sys

import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.linestring import LineString
from django.contrib.gis.geos.point import Point
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

reload(sys)
sys.setdefaultencoding('utf-8')


class InicioView(View):
    template_name = "inicio.html"

    def get(self, request):
        return render(request, self.template_name)


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
            ruta.puntos = LineString(lista)
            ruta.save()
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
    max_distance = 300  # m

    def post(self, request):
        data_post = request.data
        lat_in = data_post.get("lat_in")  # y
        lon_in = data_post.get("lon_in")  # x
        lat_go = data_post.get("lat_go")  # y
        lon_go = data_post.get("lon_go")  # x
        point_of_user = GEOSGeometry("POINT({} {})".format(lon_in, lat_in))
        point_to_go = GEOSGeometry("POINT({} {})".format(lon_go, lat_go))

        # revisa si se puede llegar en una sola ruta
        rutas_salida = Ruta.objects.filter(puntos__distance_lte=(point_of_user, Distance(m=self.max_distance)))
        rutas_salida = rutas_salida.filter(puntos__distance_lte=(point_to_go, Distance(m=self.max_distance)))

        # en caso de no poder intenta encontrar una ruta que transborde
        if len(rutas_salida) <= 0:
            rutas_salida = self.transborde(point_of_user, point_to_go)
            return Response(data=rutas_salida, status=200)

        # ruta = None
        rutas_to_send = []
        for ruta in rutas_salida:
            obj = {"id": ruta.pk, "nombre": ruta.nombre, "url": str(ruta.http_kml), "kml": str(ruta.kml)}
            rutas_to_send.append(obj)

        if len(rutas_to_send) > 0:
            return Response(data=rutas_to_send, status=200)
        else:
            rutas_to_send = self.transborde(point_of_user, point_to_go)
            return Response(data=rutas_to_send, status=200)

    def transborde(self, punto_partida, punto_final):
        rutas_salida = Ruta.objects.filter(puntos__distance_lte=(punto_partida, Distance(m=self.max_distance)))
        ruta_llegada = Ruta.objects.filter(puntos__distance_lte=(punto_final, Distance(m=self.max_distance)))
        llegadas_ids = ruta_llegada.values_list('id', flat=True)
        opciones = []
        for ruta in rutas_salida:
            print ruta
            crosses = Ruta.objects.filter(puntos__intersects=ruta.puntos, pk__in=llegadas_ids)
            ruta_obj = {}
            if len(crosses) > 0:
                ruta_obj["nombre"] = ruta.nombre
                ruta_obj["url"] = ruta.http_kml
                ruta_obj["kml"] = str(ruta.kml)
                ruta_obj["id"] = str(ruta.pk)
                opcion = []

                for cross in crosses:
                    cross_obj = {}
                    cross_obj["nombre"] = cross.nombre
                    cross_obj["url"] = cross.http_kml
                    cross_obj["kml"] = str(cross.kml)
                    cross_obj["id"] = str(cross.pk)

                    opcion.append(cross_obj)

                ruta_obj["transborde"] = opcion

                opciones.append(ruta_obj)
        return opciones

    def checas_rutas(self, id, rutas):
        for ruta in rutas:
            if ruta.get("id") == id:
                return True
        return False


class SteperByRoutes(APIView):
    def post(self, request):
        data_post = request.data
        lat_go = data_post.get("lat_go", "")
        lon_go = data_post.get("lon_go", "")
        lat_in = data_post.get("lat_in", "")
        lon_in = data_post.get("lon_in", "")
        ruta_a = data_post.get("ruta_a", None)
        ruta_b = data_post.get("ruta_b", None)

        url = "https://maps.googleapis.com/maps/api/geocode/json?latlng={}," \
              "{}&key=AIzaSyB2aJkKwaakfAgYg7mx_eol3-4iPFYdWXw "

        # section to get places (a - b)
        # point where i finish
        url_go = url.format(lat_go, lon_go)
        print "allá voy -> ", url_go
        request_go = requests.request("get", url_go)
        json_go = request_go.json()
        place_go = json_go.get("results")[0].get("formatted_address")

        # point where i start
        url_in = url.format(lat_in, lon_in)
        print "aqui empiezo ->", url_in
        request_in = requests.request("get", url_in)
        json_in = request_in.json()
        place_in = json_in.get("results")[0].get("formatted_address")

        # section to cross routes

        # get route a second route
        ruta_go = Ruta.objects.get(id=ruta_a)
        puntos_go = ruta_go.puntos

        # get route b first route
        ruta_in = Ruta.objects.get(id=ruta_b)
        puntos_in = ruta_in.puntos

        # get intersections points
        array_nodos = puntos_in.intersection(puntos_go).tuple
        array_nodos_clean = []
        for nodo in array_nodos:
            if type(nodo[0]) is tuple:
                array_nodos_clean.append(nodo[0])
            else:
                array_nodos_clean.append(nodo)

        array_nodos = array_nodos_clean

        print array_nodos[0]
        ls = LineString(array_nodos)
        ls.set_srid(4326)
        ls.transform(3857)
        print ls.length
        print ls.num_points

        # distance / puntos = distancia entre puntos
        nodos_opcionales = []
        if (ls.length / ls.num_points) > 200:
            print "puntos distantes, buscar mejor opción"
            pointfirst = Point(array_nodos[0])
            pointfirst.set_srid(4326)
            pointfirst.transform(3857)
            for nodo in array_nodos:
                nodo_compare = Point(nodo)
                nodo_compare.set_srid(4326)
                nodo_compare.transform(3857)
                distance = nodo_compare.distance(pointfirst)
                # si esta separado o es el mismo lo agregamos como opcion
                if distance > 500 or distance == 0:
                    url_in = url.format(nodo[1], nodo[0])
                    request_in = requests.request("get", url_in)
                    json_in = request_in.json()
                    place_middle = json_in.get("results")[0].get("formatted_address")
                    punto_obj = {
                        "lat": nodo[0],
                        "lon": nodo[1],
                        "name": place_middle
                    }
                    nodos_opcionales.append(punto_obj)
                    print place_middle

        else:
            nodo = array_nodos[0]
            url_in = url.format(nodo[1], nodo[0])
            request_in = requests.request("get", url_in)
            json_in = request_in.json()
            place_middle = json_in.get("results")[0].get("formatted_address")
            punto_obj = {
                "lat": nodo[0],
                "lon": nodo[1],
                "name": place_middle
            }
            nodos_opcionales.append(punto_obj)

        # define response object
        resp_obj = {
            "punto_a": {"lugar": place_in, "ruta": ruta_in.nombre},
            "punto_b": {"lugar": place_go, "ruta": ruta_go.nombre},
            "puntos_x": nodos_opcionales
        }
        resp = self.create_steps(resp_obj)
        return JsonResponse(resp, safe=False)

    def create_steps(self, objs):
        pasos = []
        obj_a = objs["punto_a"]
        obj_b = objs["punto_b"]
        obj_x = objs["puntos_x"]

        step = {"step": "Estas en {} ".format(obj_a["lugar"].split(",")[0])}
        pasos.append(step)
        step = {"step": "Toma la ruta {} ".format(obj_a["ruta"])}
        pasos.append(step)

        for punto in obj_x:
            step = {"step": "Baja en {}".format(punto["name"].split(",")[0])}
            pasos.append(step)

        step = {"step": "Toma la linea {} ".format(obj_b["ruta"])}
        pasos.append(step)
        step = {"step": "Te llevara hasta {}".format(obj_b["lugar"].split(",")[0])}
        pasos.append(step)

        return pasos
