# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-31 20:00
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('bb', '0003_auto_20160517_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='throw',
            name='event_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 5, 31, 20, 0, 20, 78000, tzinfo=utc)),
        ),
    ]
