# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-12 15:49
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('bb', '0013_auto_20160612_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='throw',
            name='event_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 12, 15, 49, 36, 92000, tzinfo=utc)),
        ),
    ]
