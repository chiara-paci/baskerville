# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-05 15:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0033_categorypersonrelation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comic',
            fields=[
                ('issue_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bibliography.Issue')),
            ],
            bases=('bibliography.issue',),
        ),
        migrations.CreateModel(
            name='ComicAuthorRelation',
            fields=[
                ('authorrelation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bibliography.AuthorRelation')),
                ('pos', models.PositiveIntegerField()),
                ('comic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bibliography.Comic')),
            ],
            options={
                'ordering': ['pos'],
            },
            bases=('bibliography.authorrelation', models.Model),
        ),
        migrations.AddField(
            model_name='comic',
            name='authors',
            field=models.ManyToManyField(blank=True, through='bibliography.ComicAuthorRelation', to='bibliography.Author'),
        ),
    ]
