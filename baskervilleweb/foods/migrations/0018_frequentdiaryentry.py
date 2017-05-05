# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foods', '0017_product_high_processed'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrequentDiaryEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('measure_unit', models.ForeignKey(to='foods.MeasureUnit')),
                ('product', models.ForeignKey(to='foods.Product')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
