# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0026_auto_20151110_1703'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='author',
            table='bibliography_author',
        ),
    ]