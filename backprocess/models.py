# -*- coding: utf-8 -*-
from __future__ import unicode_literals



# Create your models here.
from django.db import models
from django.contrib.gis.db import models as models_postgis


class Linea(models.Model):
    nombre = models.CharField(max_length=30)
    color = models.CharField(max_length=10)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = "Line"
        verbose_name_plural = "Lineas"

class Ruta(models.Model):
    nombre = models.CharField(max_length=50)
    color = models.CharField(max_length=10)
    kml = models.FileField(upload_to="kml_files")
    http_kml = models.CharField(max_length=250,)
    puntos = models_postgis.LineStringField(null=True)
    linea = models_postgis.ForeignKey(Linea, null=True)

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


class NodosRutas(models_postgis.Model):
    ruta_a = models_postgis.ForeignKey(Ruta, related_name="ruta_nodo_a")
    ruta_b = models_postgis.ForeignKey(Ruta, related_name="ruta_nodo_b")
    nodo = models_postgis.PointField()

    class Meta:
        verbose_name = "Nodo"
        verbose_name_plural = "Nodos"

    def __unicode__(self):
        return "{} | {}".format(self.ruta_a.nombre,self.ruta_b.nombre)


class RutaCoordenda(models_postgis.Model):
    ruta = models_postgis.ForeignKey(Ruta)
    coordenadas = models_postgis.PointField()
    # linea = models_postgis.LineStringField(null=True)

    def distance(self, point):
        return self.coordenadas.distance(point) * 100

    def __unicode__(self):
        return self.ruta.nombre

class TrackUsuario(models_postgis.Model):
    latlng = models_postgis.PointField()
    fecha = models_postgis.DateTimeField()

    def __unicode__(self):
        return self.ruta.fecha