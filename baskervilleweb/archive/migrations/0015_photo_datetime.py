# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-16 12:30
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0014_auto_20170516_1359'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 16, 12, 30, 18, 695302, tzinfo=utc)),
        ),
    ]
