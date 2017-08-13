# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-15 17:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0003_auto_20170506_0921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personnamerelation',
            name='value',
            field=models.CharField(db_index=True, default='-', max_length=4096),
        ),
        migrations.AlterField(
            model_name='publisherisbn',
            name='isbn',
            field=models.CharField(db_index=True, max_length=4096, unique=True),
        ),
        migrations.AlterIndexTogether(
            name='book',
            index_together=set([('isbn_ced', 'isbn_book')]),
        ),
    ]