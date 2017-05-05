# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0016_recipe_total_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='high_processed',
            field=models.BooleanField(default=False),
        ),
    ]
