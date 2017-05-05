# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0020_auto_20151110_1602'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AuthorCache',
            new_name='PersonCache',
        ),
        migrations.AlterModelTable(
            name='personcache',
            table=None,
        ),
    ]
