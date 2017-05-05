# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0014_auto_20150619_1618'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
                ('time', models.DateTimeField(default=datetime.datetime.now)),
                ('final_weight', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='RecipeProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('measure_unit', models.ForeignKey(to='foods.MeasureUnit')),
            ],
        ),
        migrations.AlterModelOptions(
            name='fooddiaryentry',
            options={'ordering': ['time']},
        ),
        migrations.AlterField(
            model_name='product',
            name='added_sugar',
            field=models.FloatField(default=0.0, blank=True, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='alcohol',
            field=models.FloatField(default=0.0, blank=True, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='fiber',
            field=models.FloatField(default=0.0, blank=True, verbose_name=b'fiber (g)', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='potassium',
            field=models.FloatField(default=0.0, blank=True, verbose_name=b'potassium (g)', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='salt',
            field=models.FloatField(default=0.0, blank=True, verbose_name=b'salt (g)', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='sodium',
            field=models.FloatField(default=0.0, blank=True, verbose_name=b'sodium (g)', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='water',
            field=models.FloatField(default=0.0, blank=True, verbose_name=b'water (ml)', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AddField(
            model_name='recipeproduct',
            name='product',
            field=models.ForeignKey(to='foods.Product'),
        ),
        migrations.AddField(
            model_name='recipeproduct',
            name='recipe',
            field=models.ForeignKey(to='foods.Recipe'),
        ),
    ]
