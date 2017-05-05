# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0010_auto_20151106_1129'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryLanguageRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.ForeignKey(to='bibliography.Category')),
                ('language', models.ForeignKey(to='bibliography.LanguageVariety')),
            ],
        ),
        migrations.AlterField(
            model_name='languagefamilyfamilyrelation',
            name='child',
            field=models.ForeignKey(related_name='parent_set', to='bibliography.LanguageFamily'),
        ),
        migrations.AlterField(
            model_name='languagefamilyfamilyrelation',
            name='parent',
            field=models.ForeignKey(related_name='child_set', to='bibliography.LanguageFamily'),
        ),
    ]
