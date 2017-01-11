# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0029_auto_20151110_1719'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Author2',
        ),
        migrations.AlterField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(to='bibliography.Author', through='bibliography.ArticleAuthorRelation', blank=True),
        ),
        migrations.AlterField(
            model_name='authorrelation',
            name='author',
            field=models.ForeignKey(to='bibliography.Author'),
        ),
        migrations.AlterField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(to='bibliography.Author', through='bibliography.BookAuthorRelation', blank=True),
        ),
        migrations.AlterField(
            model_name='migrauthor',
            name='author',
            field=models.ForeignKey(to='bibliography.Author'),
        ),
    ]
