# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-09 18:44
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backprocess', '0009_rutacoordenda_linea'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nodosrutas',
            name='nodo',
            field=django.contrib.gis.db.models.fields.PointField(default='', srid=4326),
        ),
    ]
