# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-11 07:36
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('bb', '0011_auto_20160611_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='throw',
            name='event_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 11, 7, 36, 23, 82000, tzinfo=utc)),
        ),
    ]
