# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-06 17:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('installations', '0003_auto_20160823_0956'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='installation',
            options={'ordering': ('name',)},
        ),
    ]