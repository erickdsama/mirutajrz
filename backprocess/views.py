# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.point import Point
from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.dateparse import parse_datetime

from backprocess.models import TrackUsuario


class RutasLineas(APIView):

    def post(self, request):

        return JsonResponse({}, safe=False)


class SyncTrack(APIView):

    def post(self, request):
        data_post = request.data

        # empeazmos a tomar los datos
        logs = data_post.get("logs",[])
        try:
            data_created = []
            for log in logs:
                latlng = log.get("latlng","")
                date_s = log.get("date","")
                date_d  = parse_datetime(date_s)

                latlng_clean = str(latlng).replace("(","").replace(")","")
                latlng_ar = latlng_clean.split(",")

                lat = latlng_ar[0]
                lon = latlng_ar[1]

                latlng = GEOSGeometry("POINT({} {})".format(str(lon), str(lat)))

                obj = TrackUsuario.objects.create(latlng=latlng, fecha=date_d)

            data = {
                "created": data_created
            }
            return Response(data=data, status=200)
        except Exception as e:
            print e
            data = {
                "error": e.message,
                "data": e
            }
            return Response(data=data, status=200)

