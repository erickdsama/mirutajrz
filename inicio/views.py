# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View


class InicioView(View):
    template_name = "inicio.html"

    def get(self, request):
        return render(request,self.template_name)

