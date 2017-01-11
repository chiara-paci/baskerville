# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0004_fooddiaryentry_future'),
    ]

    operations = [
        migrations.CreateModel(
            name='MicroNutrientClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
