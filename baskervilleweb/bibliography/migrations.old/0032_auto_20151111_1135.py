# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0031_auto_20151111_1130'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bibliography.person',),
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
