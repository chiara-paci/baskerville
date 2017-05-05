# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0004_auto_20151104_1636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorytimespanrelation',
            name='category',
            field=models.ForeignKey(to='bibliography.Category'),
        ),
    ]
