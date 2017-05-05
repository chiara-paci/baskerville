# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0024_author_names'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author2',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bibliography.author',),
        ),
    ]
