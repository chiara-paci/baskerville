# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0012_auto_20151109_1033'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datemodifier',
            options={'ordering': ['pos']},
        ),
        migrations.AlterModelOptions(
            name='timepoint',
            options={'ordering': ['modifier', 'date']},
        ),
        migrations.RemoveField(
            model_name='timepoint',
            name='system',
        ),
        migrations.DeleteModel(
            name='DateSystem',
        ),
    ]
