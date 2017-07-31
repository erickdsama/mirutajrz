# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from backprocess.models import Ruta, DetalleRuta, InfoRutaUsuario

admin.site.register({Ruta, DetalleRuta, InfoRutaUsuario})