# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-17 10:36
from __future__ import unicode_literals

from django.db import migrations, models
from archive import models as archive_models

class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0017_auto_20170516_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='full_path',
            field=models.FilePathField(max_length=1024, path=archive_models.PHOTO_ARCHIVE_FULL, recursive=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='thumb_path',
            field=models.FilePathField(max_length=1024, path=archive_models.PHOTO_ARCHIVE_THUMB, recursive=True),
        ),
    ]
