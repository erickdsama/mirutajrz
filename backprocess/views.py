# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView


class RutasLineas(APIView):

    def post(self, request):

        return JsonResponse({}, safe=False)


class SyncTrack(APIView):

    def post(self, request):

        return JsonResponse({}, safe=False)
