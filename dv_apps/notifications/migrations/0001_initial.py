# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-07-26 17:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emailed', models.NullBooleanField()),
                ('readnotification', models.NullBooleanField()),
                ('object_type', models.IntegerField(db_column='type')),
                ('objectid', models.BigIntegerField(blank=True, null=True)),
                ('senddate', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'usernotification',
                'managed': False,
            },
        ),
    ]
