# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-06 22:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20180707_0308'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productdiscount',
            name='customer',
        ),
    ]
