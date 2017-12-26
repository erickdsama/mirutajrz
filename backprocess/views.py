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

        return Response(data={}, status=200)
