# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-16 11:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0010_auto_20170516_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='exiftype',
            name='short',
            field=models.CharField(default='a', max_length=128),
            preserve_default=False,
        ),
    ]