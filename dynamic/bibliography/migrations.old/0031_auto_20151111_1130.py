# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0030_auto_20151111_1128'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Author',
            new_name='Person',
        ),
        migrations.AlterModelTable(
            name='person',
            table='bibliography_person',
        ),

        migrations.AlterField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(to='bibliography.Person', through='bibliography.ArticleAuthorRelation', blank=True),
        ),
        migrations.AlterField(
            model_name='authorrelation',
            name='author',
            field=models.ForeignKey(to='bibliography.Person'),
        ),
        migrations.AlterField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(to='bibliography.Person', through='bibliography.BookAuthorRelation', blank=True),
        ),
        migrations.AlterField(
            model_name='migrauthor',
            name='author',
            field=models.ForeignKey(to='bibliography.Person'),
        ),
        migrations.AlterField(
            model_name='personnamerelation',
            name='person',
            field=models.ForeignKey(to='bibliography.Person'),
        ),
    ]
