# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-15 10:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeside_server', '0015_auto_20161214_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='audio_duration',
            field=models.FloatField(blank=True, null=True, verbose_name='duration'),
        ),
    ]
