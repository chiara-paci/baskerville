# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0019_auto_20151109_1331'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='authorcache',
            table='bibliography_authorcache',
        ),
    ]
