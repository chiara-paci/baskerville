# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0014_auto_20151109_1042'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timepoint',
            options={'ordering': ['modifier', 'y_date']},
        ),
        migrations.RemoveField(
            model_name='timepoint',
            name='date',
        ),
    ]
