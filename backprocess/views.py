# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
        # datos que llegan
        print "*"*30
        print data_post
        print "*"*30

        print """
            Tomando los datos :P
        """
        # empeazmos a tomar los datos
        logs = data_post.get("logs",[])
        print "*"*30
        print logs
        print "*"*30

        data_created = []
        for log in logs:
            latlng = log.get("latlng","")
            date_s = log.get("date","")
            date_d  = parse_datetime(date_s)

            print date_d

            obj = TrackUsuario.objects.create(latlng=latlng, fecha=date_d)
            data_created.append(obj)

        data = {
            "created": data_created
        }


        return Response(data=data, status=200)
