# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0011_auto_20151106_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='datemodifier',
            name='pos',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='languagevariety',
            name='name',
            field=models.CharField(max_length=4096, blank=True),
        ),
    ]
