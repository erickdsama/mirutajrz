# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Ruta(models.Model):
    nombre = models.CharField(max_length=50)
    color = models.CharField(max_length=10)
    kml = models.FileField(upload_to="kml_files")

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas"


class InfoRutaUsuario(models.Model):
    ruta = models.ForeignKey(Ruta)
    t_espera = models.IntegerField(default=0)
    t_total = models.IntegerField(default=0)
    rating = models.IntegerField(default=5)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = "Información de usuario"
        verbose_name_plural = "Información de usuarios"


class DetalleRuta(models.Model):
    ruta = models.ForeignKey(Ruta)
    t_espera = models.IntegerField(default=0)
    t_total = models.IntegerField(default=0)
    detalle = models.TextField(null=True)

    class Meta:
        verbose_name = "Detalle ruta"
        verbose_name_plural = "Detalle de rutas"


class RutaCoordenda(models.Model):
    ruta = models.ForeignKey(Ruta)
    coordenadas = models.CharField(max_length=150)

    def __unicode__(self):
        return self.coordenadas