# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0025_author2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(to='bibliography.Author2', through='bibliography.ArticleAuthorRelation', blank=True),
        ),
        migrations.AlterField(
            model_name='authorrelation',
            name='author',
            field=models.ForeignKey(to='bibliography.Author2'),
        ),
        migrations.AlterField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(to='bibliography.Author2', through='bibliography.BookAuthorRelation', blank=True),
        ),
        migrations.AlterField(
            model_name='migrauthor',
            name='author',
            field=models.ForeignKey(to='bibliography.Author2'),
        ),
    ]
