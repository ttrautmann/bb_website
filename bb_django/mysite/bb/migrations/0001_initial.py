# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('player_name', models.CharField(max_length=15)),
                ('image_url', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Throw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result', models.IntegerField()),
                ('eventtime', models.DateTimeField(verbose_name=datetime.datetime(2016, 4, 29, 15, 40, 49, 793978, tzinfo=utc))),
                ('player', models.ForeignKey(to='bb.Player')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
