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
        verbose_name_plural = "Rustas"


class InfoRutaUsuario(models.Model):
    ruta = models.ForeignKey(Ruta)
    t_espera = models.IntegerField(default=0)
    t_total = models.IntegerField(default=0)
    rating = models.IntegerField(default=5)


class DetalleRuta(models.Model):
    ruta = models.ForeignKey(Ruta)
    t_espera = models.IntegerField(default=0)
    t_total = models.IntegerField(default=0)
    detalle = models.TextField(null=True)

class RutaCoordendas(models.Model):
    ruta = models.ForeignKey(Ruta)
    coordenadas = models.Lat