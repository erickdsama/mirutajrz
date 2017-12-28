# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView


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


        return Response(data={}, status=200)
