# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodDiaryEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(default=datetime.datetime.now)),
                ('quantity', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('kcal', models.FloatField(editable=False)),
                ('fat', models.FloatField(editable=False)),
                ('saturated_fat', models.FloatField(editable=False)),
                ('carbohydrate', models.FloatField(editable=False)),
                ('sugar', models.FloatField(editable=False)),
                ('protein', models.FloatField(editable=False)),
            ],
            options={
                'ordering': ['-time'],
            },
        ),
        migrations.CreateModel(
            name='MeasureUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
                ('base', models.CharField(default=b'g', max_length=128, choices=[(b'g', b'g'), (b'ml', b'ml')])),
                ('factor', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MicroNutrient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
                ('value_for', models.CharField(default=b'100 g', max_length=128, choices=[(b'100 g', b'100 g'), (b'100 ml', b'100 ml')])),
                ('kcal', models.PositiveIntegerField()),
                ('fat', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('saturated_fat', models.FloatField(default=0.0, blank=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('carbohydrate', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('sugar', models.FloatField(default=0.0, blank=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('protein', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
            ],
            options={
                'ordering': ['vendor', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ProductMicroNutrient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.FloatField(verbose_name=b'quantity (g)', validators=[django.core.validators.MinValueValidator(0.0)])),
                ('micro_nutrient', models.ForeignKey(to='foods.MicroNutrient')),
                ('product', models.ForeignKey(to='foods.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='WeightDiaryEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(default=datetime.datetime.now)),
                ('weight', models.FloatField(verbose_name=b'weight (kg)', validators=[django.core.validators.MinValueValidator(0.0)])),
                ('base', models.FloatField(editable=False)),
                ('need', models.FloatField(editable=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='micro_nutrients',
            field=models.ManyToManyField(to='foods.MicroNutrient', through='foods.ProductMicroNutrient', blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='vendor',
            field=models.ForeignKey(to='foods.Vendor'),
        ),
        migrations.AddField(
            model_name='fooddiaryentry',
            name='measure_unit',
            field=models.ForeignKey(to='foods.MeasureUnit'),
        ),
        migrations.AddField(
            model_name='fooddiaryentry',
            name='product',
            field=models.ForeignKey(to='foods.Product'),
        ),
        migrations.AddField(
            model_name='fooddiaryentry',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
