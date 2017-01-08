# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('bb', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='throw',
            name='eventtime',
        ),
        migrations.AddField(
            model_name='throw',
            name='event_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 29, 15, 49, 12, 558327, tzinfo=utc)),
            preserve_default=True,
        ),
    ]
