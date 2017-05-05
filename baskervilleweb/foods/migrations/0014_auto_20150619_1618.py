# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0013_auto_20150619_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooddiaryentry',
            name='fiber',
            field=models.FloatField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fooddiaryentry',
            name='potassium',
            field=models.FloatField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fooddiaryentry',
            name='salt',
            field=models.FloatField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fooddiaryentry',
            name='sodium',
            field=models.FloatField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fooddiaryentry',
            name='water',
            field=models.FloatField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='salt',
            field=models.FloatField(default=0.0, verbose_name=b'salt (g)', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='sodium',
            field=models.FloatField(default=0.0, verbose_name=b'sodium (g)', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
