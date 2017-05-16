# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='micronutrient',
            name='rda',
            field=models.FloatField(default=0.0, verbose_name=b'rda (mg)', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='productmicronutrient',
            name='quantity',
            field=models.FloatField(verbose_name=b'quantity (mg)', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
