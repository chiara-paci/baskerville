# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-17 15:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipebook', '0003_food_plural'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='tools',
            field=models.ManyToManyField(blank=True, to='recipebook.Tool'),
        ),
    ]