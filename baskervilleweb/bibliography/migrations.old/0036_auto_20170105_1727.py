# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-05 16:27


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bibliography', '0035_auto_20170105_1643'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ['date']},
        ),
        migrations.AddField(
            model_name='publication',
            name='date_format',
            field=models.CharField(default=b'%Y-%m-%d', max_length=4096),
        ),
    ]
