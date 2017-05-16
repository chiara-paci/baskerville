# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0023_auto_20151110_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='names',
            field=models.ManyToManyField(to='bibliography.NameType', through='bibliography.PersonNameRelation', blank=True),
        ),
    ]
