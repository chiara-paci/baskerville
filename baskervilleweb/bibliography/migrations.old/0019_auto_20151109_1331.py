# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0018_datemodifier_reverse'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='timepoint',
            unique_together=set([('modifier', 'date')]),
        ),
    ]
