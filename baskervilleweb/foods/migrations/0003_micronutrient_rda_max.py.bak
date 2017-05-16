# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0002_auto_20150611_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='micronutrient',
            name='rda_max',
            field=models.FloatField(default=0.0, verbose_name=b'rda max (mg)', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
