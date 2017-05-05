# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0009_usdanndfoodgroup'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsdaNndFood',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('usda_id', models.CharField(max_length=1024)),
                ('long_description', models.CharField(max_length=1024)),
                ('short_description', models.CharField(max_length=1024)),
                ('common_name', models.CharField(max_length=1024)),
                ('manufacturer_name', models.CharField(max_length=1024)),
                ('survey', models.BooleanField()),
                ('refuse_desc', models.CharField(max_length=1024)),
                ('refuse_perc', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('scientific_name', models.CharField(max_length=1024)),
                ('nitrogen_factor', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('protein_factor', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('fat_factor', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('carbohydrate_factor', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('food_group', models.ForeignKey(to='foods.UsdaNndFoodGroup')),
            ],
        ),
    ]
